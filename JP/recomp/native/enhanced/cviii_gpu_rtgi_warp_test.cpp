/* ROM-free Windows WARP execution test for the EXACT embedded CS5.0 shader.
 * WARP is Microsoft software D3D11; playable GPU mode still requires
 * hardware D3D11. No ROM or SDL2 window is necessary to dispatch this test.
 */
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <d3d11.h>
#include <d3dcompiler.h>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <cmath>
#include <vector>
extern "C" int cviii_rc_apply(ID3D11Device*,ID3D11DeviceContext*,
    ID3D11ShaderResourceView*,ID3D11ShaderResourceView*,
    ID3D11UnorderedAccessView*,unsigned,unsigned);
#include "cviii_gpu_rtgi_shader_hlsl.h"
#pragma comment(lib,"d3d11.lib")
#pragma comment(lib,"d3dcompiler.lib")
struct L {float pos[4],color[4],dir[4],anim[4];};
struct W {float bounds[4],attrs[4],alb[4];};
struct XY {int x,y;};
struct Params {uint32_t lights,walls,frame,pad;float ambientSky[4],sky[4],grade[4];};
static_assert(sizeof(L)==64 && sizeof(W)==48 && sizeof(XY)==8 && sizeof(Params)==64);
template<typename T> void drop(T*&v){if(v){v->Release();v=nullptr;}}
int main(){
 ID3D11Device *dev=nullptr;ID3D11DeviceContext *ctx=nullptr;
 ID3D11ComputeShader *shader=nullptr;
 ID3DBlob *compiled=nullptr,*errors=nullptr;
 const D3D_FEATURE_LEVEL levels[]={D3D_FEATURE_LEVEL_11_0};
 D3D_FEATURE_LEVEL level;
 HRESULT hr=D3D11CreateDevice(nullptr,D3D_DRIVER_TYPE_WARP,nullptr,0,
   levels,1,D3D11_SDK_VERSION,&dev,&level,&ctx);
 if(FAILED(hr)){
   std::puts("SKIP WARP unavailable on runner (HLSL compilation still separately tested)");
   return 0;
 }
 hr=D3DCompile(cviii_gpu_hlsl,strlen(cviii_gpu_hlsl),nullptr,nullptr,nullptr,
   "main","cs_5_0",D3DCOMPILE_OPTIMIZATION_LEVEL3,0,&compiled,&errors);
 if(FAILED(hr) || !compiled){
   std::fprintf(stderr,"GPU shader compiler failed during execution smoke\n");
   drop(errors);drop(ctx);drop(dev);return 1;
 }
 hr=dev->CreateComputeShader(compiled->GetBufferPointer(),
                             compiled->GetBufferSize(),nullptr,&shader);
 drop(compiled);drop(errors);
 if(FAILED(hr)){drop(ctx);drop(dev);return 1;}
 auto buffer=[&](UINT bytes,UINT bind,UINT misc,UINT stride,
                 D3D11_USAGE usage,UINT cpu,ID3D11Buffer **output)->bool{
   D3D11_BUFFER_DESC d{};d.ByteWidth=bytes;d.BindFlags=bind;
   d.MiscFlags=misc;d.StructureByteStride=stride;
   d.Usage=usage;d.CPUAccessFlags=cpu;
   return SUCCEEDED(dev->CreateBuffer(&d,nullptr,output));
 };
 ID3D11Buffer *lights=nullptr,*walls=nullptr,*scan=nullptr,*uniform=nullptr,
              *output=nullptr,*readback=nullptr;
 constexpr UINT count=128*96;
 const UINT str=D3D11_RESOURCE_MISC_BUFFER_STRUCTURED;
 bool ok=buffer(sizeof(L),D3D11_BIND_SHADER_RESOURCE,str,sizeof(L),
                  D3D11_USAGE_DYNAMIC,D3D11_CPU_ACCESS_WRITE,&lights)
    && buffer(sizeof(W),D3D11_BIND_SHADER_RESOURCE,str,sizeof(W),
                  D3D11_USAGE_DYNAMIC,D3D11_CPU_ACCESS_WRITE,&walls)
    && buffer(sizeof(XY)*96,D3D11_BIND_SHADER_RESOURCE,str,sizeof(XY),
                  D3D11_USAGE_DYNAMIC,D3D11_CPU_ACCESS_WRITE,&scan)
    && buffer(sizeof(Params),D3D11_BIND_CONSTANT_BUFFER,0,0,
                  D3D11_USAGE_DYNAMIC,D3D11_CPU_ACCESS_WRITE,&uniform)
    && buffer(sizeof(float)*4*count,D3D11_BIND_UNORDERED_ACCESS,
                  str,sizeof(float)*4,D3D11_USAGE_DEFAULT,0,&output)
    && buffer(sizeof(float)*4*count,0,0,0,D3D11_USAGE_STAGING,
                  D3D11_CPU_ACCESS_READ,&readback);
 if(!ok){std::fputs("WARP allocation failed\n",stderr);return 1;}
 auto upload=[&](ID3D11Buffer *target,const void *data,size_t bytes)->bool{
   D3D11_MAPPED_SUBRESOURCE m{};
   if(FAILED(ctx->Map(target,0,D3D11_MAP_WRITE_DISCARD,0,&m)))return false;
   memcpy(m.pData,data,bytes);ctx->Unmap(target,0);return true;
 };
 ID3D11ShaderResourceView *srv[3]={nullptr,nullptr,nullptr};
 ID3D11UnorderedAccessView *uav=nullptr;
 auto makeview=[&](ID3D11Buffer *b,UINT n,ID3D11ShaderResourceView **v)->bool{
   D3D11_SHADER_RESOURCE_VIEW_DESC d{};
   d.Format=DXGI_FORMAT_UNKNOWN;d.ViewDimension=D3D11_SRV_DIMENSION_BUFFER;
   d.Buffer.NumElements=n;
   return SUCCEEDED(dev->CreateShaderResourceView(b,&d,v));
 };
 ok=makeview(lights,1,&srv[0])&&makeview(walls,1,&srv[1])
    &&makeview(scan,96,&srv[2]);
 D3D11_UNORDERED_ACCESS_VIEW_DESC desc{};
 desc.Format=DXGI_FORMAT_UNKNOWN;desc.ViewDimension=D3D11_UAV_DIMENSION_BUFFER;
 desc.Buffer.NumElements=count;
 ok=ok && SUCCEEDED(dev->CreateUnorderedAccessView(output,&desc,&uav));
 if(!ok){std::fputs("WARP SRV/UAV creation failed\n",stderr);return 1;}
 XY rows[96]{};for(int y=0;y<96;++y){rows[y].x=0;rows[y].y=48+y*2;}
 L light{};light.pos[0]=64;light.pos[1]=120;light.pos[2]=135;light.pos[3]=100;
 light.color[0]=1;light.color[1]=0.3f;light.color[2]=0.1f;
 light.dir[0]=1;light.dir[2]=0.57f;light.dir[3]=32;
 light.anim[0]=1;light.anim[1]=1;light.anim[2]=1;
 W w{};w.bounds[0]=88;w.bounds[1]=90;w.bounds[2]=10;w.bounds[3]=60;
 w.attrs[0]=1;w.attrs[1]=3;w.attrs[2]=87.75f;w.attrs[3]=120;
 Params args{};args.lights=1;args.walls=0;args.ambientSky[0]=.7f;
 args.ambientSky[1]=.7f;args.ambientSky[2]=.7f;
 args.sky[0]=1;args.sky[1]=1;args.sky[2]=1;args.grade[0]=1;
 args.grade[2]=1;
 if(!upload(lights,&light,sizeof light)||!upload(walls,&w,sizeof w)||
    !upload(scan,rows,sizeof rows))return 1;
 auto dispatch=[&](float &inside,float &behind,float &bounce)->bool{
    if(!upload(uniform,&args,sizeof args))return false;
    ctx->CSSetShader(shader,nullptr,0);
    ctx->CSSetShaderResources(0,3,srv);
    ctx->CSSetConstantBuffers(0,1,&uniform);
    ctx->CSSetUnorderedAccessViews(0,1,&uav,nullptr);
    ctx->Dispatch(16,12,1);
    ID3D11ShaderResourceView *none[3]={nullptr,nullptr,nullptr};
    ID3D11UnorderedAccessView *noUav=nullptr;
    ctx->CSSetShaderResources(0,3,none);
    ctx->CSSetUnorderedAccessViews(0,1,&noUav,nullptr);
    ctx->CopyResource(readback,output);
    D3D11_MAPPED_SUBRESOURCE mapped{};
    if(FAILED(ctx->Map(readback,0,D3D11_MAP_READ,0,&mapped)))return false;
    const float *map=(const float*)mapped.pData;
    inside=map[4*(36*128+32)];
    behind=map[4*(36*128+60)];
    bounce=map[4*(36*128+39)];
    ctx->Unmap(readback,0);
    return std::isfinite(inside)&&std::isfinite(behind)&&std::isfinite(bounce);
 };
 float directNear=0,directBehind=0,dummy=0;
 if(!dispatch(directNear,directBehind,dummy) || directNear<=.7f ||
    directBehind<=.7f){std::fputs("WARP direct light failed\n",stderr);return 1;}
 args.walls=1;
 float shadowNear=0,shadowBehind=0,beforeBounce=0;
 if(!dispatch(shadowNear,shadowBehind,beforeBounce) ||
    !(shadowBehind<directBehind-.025f)){
   std::fprintf(stderr,"WARP ray shadow failed: %f vs %f\n",shadowBehind,directBehind);
   return 1;
 }
 // Reflection source is placed on the light-facing (left) wall face.
 w.alb[0]=.45f;w.alb[1]=.1f;w.alb[2]=.05f;
 if(!upload(walls,&w,sizeof w))return 1;
 float afterNear=0,afterBehind=0,afterBounce=0;
 if(!dispatch(afterNear,afterBehind,afterBounce) ||
    !(afterBounce>beforeBounce+.0005f)){
   std::fprintf(stderr,"WARP one bounce failed: %f vs %f\n",afterBounce,beforeBounce);
   return 1;
 }
 std::printf("PASS CVIII D3D11 WARP direct=%f shadow=%f bounced=%f\n",
             directNear,shadowBehind,afterBounce-beforeBounce);
 // Exact Radiance Cascades runtime module on WARP, levels 2/3/4. Verify
 // hierarchical probe integration contributes measurable extra bounce
 // over the proven direct + face-sampled baseline, without NaNs.
 for(unsigned quality=2;quality<=4;++quality){
    if(!dispatch(afterNear,afterBehind,afterBounce))return 1;
    std::vector<float> baseline(count*4);
    D3D11_MAPPED_SUBRESOURCE read{};
    if(FAILED(ctx->Map(readback,0,D3D11_MAP_READ,0,&read)))return 1;
    memcpy(baseline.data(),read.pData,baseline.size()*sizeof(float));
    ctx->Unmap(readback,0);
    if(!cviii_rc_apply(dev,ctx,srv[1],srv[2],uav,1,quality)){
        std::fprintf(stderr,"Radiance Cascades WARP dispatch failed at quality %u\n",quality);
        return 1;
    }
    ctx->CopyResource(readback,output);
    if(FAILED(ctx->Map(readback,0,D3D11_MAP_READ,0,&read)))return 1;
    const float *result=(const float*)read.pData;
    float additional=0.f;
    bool finite=true;
    for(unsigned j=0;j<count;++j){
        for(int c=0;c<3;++c){
            float n=result[j*4+c];
            if(!std::isfinite(n) || n<0.f || n>16.f)finite=false;
            additional+=n-baseline[j*4+c];
        }
    }
    ctx->Unmap(readback,0);
    if(!finite || additional<0.001f){
        std::fprintf(stderr,
          "Radiance Cascades quality %u invalid contribution: %f finite=%d\n",
          quality,additional,(int)finite);
        return 1;
    }
    std::printf("PASS Radiance Cascades WARP quality=%u indirect sum=%f\n",
               quality,additional);
 }
 drop(uav);for(auto &v:srv)drop(v);
 drop(readback);drop(output);drop(uniform);drop(scan);drop(walls);drop(lights);
 drop(shader);drop(ctx);drop(dev);
 return 0;
}
