/* CVIII Radiance Cascades for 2D authored masks: D3D11 shader pipeline.
 * Buffers: 2 x 6144 RGBA32F rays (fixed memory per cascade), constant
 * geometry budget and 2/3/4 cascades. Execute far to near, then integrate
 * probe-zero irradiance into existing HDR direct lightmap without GPU readback.
 * Uses the device/context of the separate owner-side GPU prototype,
 * not SDL2's window, game RAM, or ReShade's graphics context.
 */
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <d3d11.h>
#include <d3dcompiler.h>
#include <cstring>
#include "cviii_radiance_cascades_shader_hlsl.h"
namespace {
static constexpr UINT RAYS=6144;
struct Globals {UINT level,wallsCount,levelsCount,rayCount;};
ID3D11Device *owner=nullptr;
ID3D11ComputeShader *traceShader=nullptr,*resolveShader=nullptr;
ID3D11Buffer *buf[2]={nullptr,nullptr},*uniform=nullptr;
ID3D11ShaderResourceView *srv[2]={nullptr,nullptr};
ID3D11UnorderedAccessView *uav[2]={nullptr,nullptr};
static const char *status="Radiance Cascades: not initialized";
template<class T> void drop(T *&p){if(p){p->Release();p=nullptr;}}
void destroy(){
    drop(srv[0]);drop(srv[1]);drop(uav[0]);drop(uav[1]);
    drop(buf[0]);drop(buf[1]);drop(uniform);
    drop(traceShader);drop(resolveShader);
    drop(owner);
}
bool compile(ID3D11Device *device,const char *entry,ID3D11ComputeShader **dest){
    ID3DBlob *blob=nullptr,*errors=nullptr;
    HRESULT result=D3DCompile(cviii_rc_hlsl,std::strlen(cviii_rc_hlsl),
        "cviii_radiance_cascades",nullptr,nullptr,entry,"cs_5_0",
        D3DCOMPILE_OPTIMIZATION_LEVEL3,0,&blob,&errors);
    if(FAILED(result) || !blob){drop(errors);drop(blob);return false;}
    result=device->CreateComputeShader(blob->GetBufferPointer(),
                                        blob->GetBufferSize(),nullptr,dest);
    drop(errors);drop(blob);
    return SUCCEEDED(result);
}
bool initialize(ID3D11Device *device){
    if(owner==device && traceShader && resolveShader)return true;
    destroy();
    if(!device)return false;
    owner=device;owner->AddRef();
    if(!compile(device,"cascadeMain",&traceShader) ||
       !compile(device,"resolveMain",&resolveShader)){
        status="Radiance Cascades shader compile failed";
        destroy();return false;
    }
    D3D11_BUFFER_DESC desc{};
    desc.ByteWidth=sizeof(Globals);
    desc.BindFlags=D3D11_BIND_CONSTANT_BUFFER;
    desc.Usage=D3D11_USAGE_DYNAMIC;
    desc.CPUAccessFlags=D3D11_CPU_ACCESS_WRITE;
    if(FAILED(device->CreateBuffer(&desc,nullptr,&uniform))){
        status="Radiance Cascades constants allocation failed";
        destroy();return false;
    }
    for(int i=0;i<2;++i){
        D3D11_BUFFER_DESC b{};
        b.ByteWidth=RAYS*16;
        b.BindFlags=D3D11_BIND_SHADER_RESOURCE | D3D11_BIND_UNORDERED_ACCESS;
        b.MiscFlags=D3D11_RESOURCE_MISC_BUFFER_STRUCTURED;
        b.StructureByteStride=16;
        b.Usage=D3D11_USAGE_DEFAULT;
        if(FAILED(device->CreateBuffer(&b,nullptr,&buf[i]))){
            status="Radiance Cascades buffer allocation failed";destroy();return false;
        }
        D3D11_SHADER_RESOURCE_VIEW_DESC v{};
        v.Format=DXGI_FORMAT_UNKNOWN;v.ViewDimension=D3D11_SRV_DIMENSION_BUFFER;
        v.Buffer.NumElements=RAYS;
        if(FAILED(device->CreateShaderResourceView(buf[i],&v,&srv[i]))){
            status="Radiance Cascades SRV failed";destroy();return false;
        }
        D3D11_UNORDERED_ACCESS_VIEW_DESC u{};
        u.Format=DXGI_FORMAT_UNKNOWN;u.ViewDimension=D3D11_UAV_DIMENSION_BUFFER;
        u.Buffer.NumElements=RAYS;
        if(FAILED(device->CreateUnorderedAccessView(buf[i],&u,&uav[i]))){
            status="Radiance Cascades UAV failed";destroy();return false;
        }
    }
    status="Radiance Cascades ready: 2-4 hierarchical probe levels";
    return true;
}
void unbind(ID3D11DeviceContext *context){
    ID3D11ShaderResourceView *nullSrv[4]={nullptr,nullptr,nullptr,nullptr};
    ID3D11UnorderedAccessView *nullUav[2]={nullptr,nullptr};
    context->CSSetShaderResources(0,4,nullSrv);
    context->CSSetUnorderedAccessViews(0,2,nullUav,nullptr);
    context->CSSetShader(nullptr,nullptr,0);
}
}
extern "C" int cviii_rc_apply(ID3D11Device *device,ID3D11DeviceContext *context,
    ID3D11ShaderResourceView *wallView,
    ID3D11ShaderResourceView *scanView,
    ID3D11UnorderedAccessView *directLightmap,
    unsigned wallCount,unsigned quality){
    if(!device || !context || !wallView || !scanView || !directLightmap ||
       quality<2 || quality>4 || wallCount>12)return 0;
    if(!initialize(device))return 0;
    int previous=-1;
    for(int level=(int)quality-1;level>=0;--level){
        int current=level&1;
        Globals p{(UINT)level,wallCount,quality,RAYS};
        D3D11_MAPPED_SUBRESOURCE mapped{};
        if(FAILED(context->Map(uniform,0,D3D11_MAP_WRITE_DISCARD,0,&mapped))){
            status="Radiance Cascades constant upload failed";unbind(context);return 0;
        }
        std::memcpy(mapped.pData,&p,sizeof(p));
        context->Unmap(uniform,0);
        ID3D11ShaderResourceView *inputs[3]={
            wallView,scanView,previous>=0?srv[previous]:nullptr};
        context->CSSetShader(traceShader,nullptr,0);
        context->CSSetShaderResources(0,3,inputs);
        context->CSSetConstantBuffers(0,1,&uniform);
        context->CSSetUnorderedAccessViews(0,1,&uav[current],nullptr);
        context->Dispatch((RAYS+63)/64,1,1);
        ID3D11UnorderedAccessView *nullUav=nullptr;
        ID3D11ShaderResourceView *nullInput[3]={nullptr,nullptr,nullptr};
        context->CSSetUnorderedAccessViews(0,1,&nullUav,nullptr);
        context->CSSetShaderResources(0,3,nullInput);
        previous=current;
    }
    // Merge the computed probe-zero irradiance into the existing lightmap.
    // Output is bound u1, never concurrently sampled as an SRV.
    ID3D11ShaderResourceView *inner=srv[previous];
    context->CSSetShader(resolveShader,nullptr,0);
    context->CSSetShaderResources(3,1,&inner);
    context->CSSetUnorderedAccessViews(1,1,&directLightmap,nullptr);
    context->Dispatch(16,12,1);
    unbind(context);
    status=quality==2?"Radiance Cascades active: 2 levels (Low)":
           quality==3?"Radiance Cascades active: 3 levels (Medium)":
                      "Radiance Cascades active: 4 levels (High)";
    return 1;
}
extern "C" const char *cviii_rc_status(void){return status;}
extern "C" void cviii_rc_reset(void){/* Stateless per frame; no cached scene history. */}
