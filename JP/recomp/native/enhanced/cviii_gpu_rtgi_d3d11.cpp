/* CVIII Enhanced experimental GPU RTGI, Windows D3D11 compute only.
 * The existing NESRecomp + SDL2 window remains authoritative.
 * This computes a low-resolution HDR lightmap and reads it back into
 * the owner-controlled PRESENTATION copy; CPU Standard is mandatory fallback.
 * Geometry comes ONLY from explicitly authored CVIII occluder masks.
 * One indirect bounce is a face-sampled diffuse approximation, not full GI.
 * No game ROM, NES RAM, mapper state, SDL renderer state or ReShade hook.
 */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <d3d11.h>
#include <d3dcompiler.h>
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstring>
#include "cviii_gpu_rtgi.h"
#pragma comment(lib,"d3d11.lib")
#pragma comment(lib,"d3dcompiler.lib")

namespace {
constexpr int LW=128,LH=96,MAX_L=12,MAX_W=12;
struct GpuLight {
    float pos[4],rgbshape[4],direction[4],motion[4];
};
struct GpuWall {
    float bounds[4],attrs[4],reflect[4];
};
struct GpuScan {int x,y;};
struct Params {
    uint32_t lightCount,wallCount,frame,unused;
    float ambientSky[4]; /* ambient r,g,b, sky strength */
    float skyColor[4];   /* r,g,b, direction */
    float grade[4];      /* EV multiplier, warm bias, saturation, reserved */
};
static_assert(sizeof(GpuLight)==64 && sizeof(GpuWall)==48);
static_assert(sizeof(Params)%16==0);
static ID3D11Device *device=nullptr;
static ID3D11DeviceContext *context=nullptr;
static ID3D11ComputeShader *shader=nullptr;
static ID3D11Buffer *lightBuf=nullptr,*wallBuf=nullptr,*scanBuf=nullptr,
                    *paramBuf=nullptr,*lightmapBuf=nullptr,*staging=nullptr;
static ID3D11ShaderResourceView *lightView=nullptr,*wallView=nullptr,*scanView=nullptr;
static ID3D11UnorderedAccessView *lightmapView=nullptr;
static bool attempted=false;
static const char *state="D3D11 GPU: not initialized";
template<class T> void release(T *&p){if(p){p->Release();p=nullptr;}}
void close_gpu(){
    if(context){
        context->CSSetShader(nullptr,nullptr,0);
        ID3D11UnorderedAccessView *u=nullptr;
        context->CSSetUnorderedAccessViews(0,1,&u,nullptr);
        ID3D11ShaderResourceView *v[3]={nullptr,nullptr,nullptr};
        context->CSSetShaderResources(0,3,v);
    }
    release(lightmapView);release(lightView);release(wallView);release(scanView);
    release(staging);release(lightmapBuf);release(lightBuf);release(wallBuf);
    release(scanBuf);release(paramBuf);release(shader);
    release(context);release(device);
}
#include "cviii_gpu_rtgi_shader_hlsl.h"
const char *const hlsl=cviii_gpu_hlsl;
bool create_buffer(UINT bytes,UINT bind,UINT misc,UINT stride,ID3D11Buffer **out,
                   D3D11_USAGE usage=D3D11_USAGE_DYNAMIC,UINT access=D3D11_CPU_ACCESS_WRITE){
    D3D11_BUFFER_DESC d{};
    d.ByteWidth=bytes;d.BindFlags=bind;d.Usage=usage;
    d.MiscFlags=misc;d.StructureByteStride=stride;d.CPUAccessFlags=access;
    return SUCCEEDED(device->CreateBuffer(&d,nullptr,out));
}
template<class T> bool write_buffer(ID3D11Buffer *buffer,const T *data,size_t bytes){
    D3D11_MAPPED_SUBRESOURCE mapped{};
    if(FAILED(context->Map(buffer,0,D3D11_MAP_WRITE_DISCARD,0,&mapped)))return false;
    std::memcpy(mapped.pData,data,bytes);
    context->Unmap(buffer,0);
    return true;
}
bool initialize(){
    if(attempted)return device && shader;
    attempted=true;
    D3D_FEATURE_LEVEL chosen;
    const D3D_FEATURE_LEVEL levels[]={D3D_FEATURE_LEVEL_11_1,D3D_FEATURE_LEVEL_11_0};
    HRESULT hr=D3D11CreateDevice(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,
        0,levels,2,D3D11_SDK_VERSION,&device,&chosen,&context);
    if(FAILED(hr)){
        const D3D_FEATURE_LEVEL only11[]={D3D_FEATURE_LEVEL_11_0};
        hr=D3D11CreateDevice(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,
                            only11,1,D3D11_SDK_VERSION,&device,&chosen,&context);
    }
    if(FAILED(hr) || chosen<D3D_FEATURE_LEVEL_11_0){
        state="GPU unavailable: hardware D3D11 compute required";close_gpu();return false;
    }
    ID3DBlob *binary=nullptr,*errors=nullptr;
    hr=D3DCompile(hlsl,std::strlen(hlsl),nullptr,nullptr,nullptr,"main","cs_5_0",
                  D3DCOMPILE_OPTIMIZATION_LEVEL3,0,&binary,&errors);
    if(FAILED(hr)){
        state="GPU unavailable: compute shader compile failed";
        release(errors);release(binary);close_gpu();return false;
    }
    hr=device->CreateComputeShader(binary->GetBufferPointer(),
                                   binary->GetBufferSize(),nullptr,&shader);
    release(errors);release(binary);
    if(FAILED(hr)){
        state="GPU unavailable: compute shader creation failed";
        close_gpu();return false;
    }
    const UINT structured=D3D11_RESOURCE_MISC_BUFFER_STRUCTURED;
    if(!create_buffer(sizeof(GpuLight)*MAX_L,D3D11_BIND_SHADER_RESOURCE,structured,sizeof(GpuLight),&lightBuf) ||
       !create_buffer(sizeof(GpuWall)*MAX_W,D3D11_BIND_SHADER_RESOURCE,structured,sizeof(GpuWall),&wallBuf) ||
       !create_buffer(sizeof(GpuScan)*LH,D3D11_BIND_SHADER_RESOURCE,structured,sizeof(GpuScan),&scanBuf) ||
       !create_buffer(sizeof(Params),D3D11_BIND_CONSTANT_BUFFER,0,0,&paramBuf) ||
       !create_buffer(sizeof(float)*4*LW*LH,D3D11_BIND_UNORDERED_ACCESS,
                      structured,sizeof(float)*4,&lightmapBuf,D3D11_USAGE_DEFAULT,0) ||
       !create_buffer(sizeof(float)*4*LW*LH,0,0,0,&staging,
                      D3D11_USAGE_STAGING,D3D11_CPU_ACCESS_READ)){
        state="GPU unavailable: D3D11 buffer allocation failed";
        close_gpu();return false;
    }
    auto view=[](ID3D11Buffer *buf,UINT count,ID3D11ShaderResourceView **out)->bool{
        D3D11_SHADER_RESOURCE_VIEW_DESC desc{};
        desc.Format=DXGI_FORMAT_UNKNOWN;desc.ViewDimension=D3D11_SRV_DIMENSION_BUFFER;
        desc.Buffer.FirstElement=0;desc.Buffer.NumElements=count;
        return SUCCEEDED(device->CreateShaderResourceView(buf,&desc,out));
    };
    if(!view(lightBuf,MAX_L,&lightView) || !view(wallBuf,MAX_W,&wallView) ||
       !view(scanBuf,LH,&scanView)){
        state="GPU unavailable: shader resource view creation failed";
        close_gpu();return false;
    }
    D3D11_UNORDERED_ACCESS_VIEW_DESC uav{};
    uav.Format=DXGI_FORMAT_UNKNOWN;uav.ViewDimension=D3D11_UAV_DIMENSION_BUFFER;
    uav.Buffer.FirstElement=0;uav.Buffer.NumElements=LW*LH;
    if(FAILED(device->CreateUnorderedAccessView(lightmapBuf,&uav,&lightmapView))){
        state="GPU unavailable: writable lightmap creation failed";
        close_gpu();return false;
    }
    state="GPU D3D11: 128x96 direct + sampled one bounce";
    return true;
}
int unwrap(int ppu,int camera){
    int d=(ppu-camera%512+1024)%512;
    if(d>256)d-=512;
    return camera+d;
}
float clampf(float x,float a,float b){return x<a?a:(x>b?b:x);}
unsigned channel(unsigned input,float gain){
    float base=(float)input;
    float value;
    if(gain<=1.f)value=base*std::max(0.f,gain);
    else{
        float headroom=255.f-base,raise=base*(gain-1.f);
        value=base+(headroom>0.f?headroom*raise/(headroom+raise):0.f);
    }
    return (unsigned)clampf(std::floor(value+0.5f),0.f,255.f);
}
int run(const CviiiLighting *s,uint32_t *pixels,uint32_t room,int camera,
        const int sx[240],const int sy[240],uint64_t frame){
    if(!s || !pixels || !sx || !sy || !initialize())return 0;
    GpuLight lights[MAX_L]{};
    GpuWall walls[MAX_W]{};
    GpuScan lines[LH]{};
    int nlight=0,nwall=0;
    for(int i=0;i<CVIII_LIGHT_MAX;++i){
        const CviiiLight *old=&s->light[i];
        if(!old->used || old->muted || old->room!=room)continue;
        if(nlight>=MAX_L){
            state="GPU capacity exceeded: Standard fallback (12 scene lights)";
            return 0;
        }
        CviiiLight local;
        cviii_light_effective(s,old,&local);
        GpuLight &l=lights[nlight++];
        l.pos[0]=(float)local.x;l.pos[1]=(float)local.y;
        l.pos[2]=(float)local.radius;l.pos[3]=(float)local.energy;
        l.rgbshape[0]=local.red/255.f;l.rgbshape[1]=local.green/255.f;
        l.rgbshape[2]=local.blue/255.f;l.rgbshape[3]=(float)local.shape;
        float angle=(float)local.angle*0.017453292519943295f;
        l.direction[0]=std::cos(angle);l.direction[1]=std::sin(angle);
        l.direction[2]=std::tan(std::max(5,std::min(85,local.spread?local.spread:30))
                       *0.017453292519943295f);
        l.direction[3]=(float)(local.width?local.width:32);
        l.motion[0]=(float)local.flicker;
        l.motion[1]=local.anim_speed?local.anim_speed/100.f:1.f;
        l.motion[2]=local.anim_strength?local.anim_strength/100.f:1.f;
    }
    for(int i=0;i<CVIII_OCCLUDER_MAX;++i){
        const CviiiOccluder &m=s->masks[i];
        if(!m.used || m.room!=room)continue;
        if(nwall>=MAX_W){
            state="GPU capacity exceeded: Standard fallback (12 scene masks)";
            return 0;
        }
        GpuWall &w=walls[nwall++];
        w.bounds[0]=(float)m.x;w.bounds[1]=(float)m.y;
        w.bounds[2]=(float)m.w;w.bounds[3]=(float)m.h;
        w.attrs[0]=m.opacity/100.f;w.attrs[1]=(float)m.softness;
        // Estimate diffuse wall albedo from original visible palette colors.
        // When the wall is offscreen use neutral reflected color; do NOT
        // invent hidden tile materials.
        float reflectance[3]={0.35f,0.35f,0.35f};
        int bestY=120,delta=9999;
        for(int y=CVIII_LIGHT_HUD;y<240;++y){
            int d=std::abs(sy[y]-(m.y+m.h/2));
            if(d<delta){delta=d;bestY=y;}
        }
        int localX=m.x+m.w/2-unwrap(sx[bestY],camera);
        if(delta<=8 && localX>=0 && localX<256){
            uint32_t p=pixels[bestY*256+localX];
            reflectance[0]=std::max(.07f,((p>>16)&255)/255.f)*.65f;
            reflectance[1]=std::max(.07f,((p>>8)&255)/255.f)*.65f;
            reflectance[2]=std::max(.07f,(p&255)/255.f)*.65f;
        }
        // Choose the strongest lit wall face as a secondary, one-bounce
        // virtual emitter. Light transport from sources to this face is
        // evaluated only once per wall per frame, avoiding O(pixels*L*W^2).
        float illumination[3]={0,0,0};
        float strongest=0.f;
        float faceX=(float)m.x,faceY=(float)m.y+m.h*.5f;
        for(int k=0;k<nlight;++k){
            const GpuLight &src=lights[k];
            float cx=(float)m.x+m.w*.5f,cy=(float)m.y+m.h*.5f;
            float dx=src.pos[0]-cx,dy=src.pos[1]-cy;
            float px=cx,py=cy;
            if(std::fabs(dx)/(m.w?m.w:1)>std::fabs(dy)/(m.h?m.h:1)){
                px=dx>0?float(m.x+m.w)+.25f:float(m.x)-.25f;
            }else{
                py=dy>0?float(m.y+m.h)+.25f:float(m.y)-.25f;
            }
            float distance=std::hypot(src.pos[0]-px,src.pos[1]-py);
            float range=std::max(1.f,src.pos[2]);
            if(distance>range*1.5f)continue;
            int lx=(int)std::lround(src.pos[0]),ly=(int)std::lround(src.pos[1]);
            float visibility=cviii_light_shadow(s,room,lx,ly,
                                 (int)std::lround(px),(int)std::lround(py));
            // Skip the current mask geometry to estimate illumination at
            // its front-facing surface; allow walls to block other walls.
            if(visibility<.02f)visibility=.1f;
            float amount=std::max(0.f,1-distance/(1.5f*range));
            amount=src.pos[3]*.014f*amount*amount*visibility;
            for(int channel=0;channel<3;++channel)
                illumination[channel]+=amount*src.rgbshape[channel];
            if(amount>strongest){strongest=amount;faceX=px;faceY=py;}
        }
        w.attrs[2]=faceX;w.attrs[3]=faceY;
        for(int channel=0;channel<3;++channel)
            w.reflect[channel]=reflectance[channel]*
                std::min(1.5f,illumination[channel])*.24f;
    }
    for(int row=0;row<LH;++row){
        int y=CVIII_LIGHT_HUD+2*row;
        lines[row]={unwrap(sx[y],camera),sy[y]};
    }
    int ambient=0,amb[3]={255,255,255},sky=0,skyRgb[3]={186,209,255},
        skyFacing=-1;
    cviii_light_scene_get(s,room,&ambient,amb);
    cviii_light_sky_get(s,room,&sky,skyRgb,&skyFacing);
    int ev=0,temp=0,sat=100;
    cviii_light_grade_get(s,room,&ev,&temp,&sat);
    Params args{};
    args.lightCount=(uint32_t)nlight;
    args.wallCount=(uint32_t)nwall;
    args.frame=(uint32_t)(frame%216000);
    for(int c=0;c<3;++c){
        args.ambientSky[c]=ambient*amb[c]/25500.f;
        args.skyColor[c]=skyRgb[c]/255.f;
    }
    args.ambientSky[3]=(float)sky;
    args.skyColor[3]=(float)skyFacing;
    args.grade[0]=std::exp2(ev/100.f);
    args.grade[1]=temp/100.f;
    args.grade[2]=sat/100.f;
    if(!write_buffer(lightBuf,lights,sizeof lights) ||
       !write_buffer(wallBuf,walls,sizeof walls) ||
       !write_buffer(scanBuf,lines,sizeof lines) ||
       !write_buffer(paramBuf,&args,sizeof args)){
        state="GPU buffer upload failed: Standard fallback";
        return 0;
    }
    ID3D11ShaderResourceView *views[3]={lightView,wallView,scanView};
    context->CSSetShader(shader,nullptr,0);
    context->CSSetShaderResources(0,3,views);
    context->CSSetUnorderedAccessViews(0,1,&lightmapView,nullptr);
    context->CSSetConstantBuffers(0,1,&paramBuf);
    context->Dispatch((LW+7)/8,(LH+7)/8,1);
    ID3D11UnorderedAccessView *nullUav=nullptr;
    ID3D11ShaderResourceView *nullView[3]={nullptr,nullptr,nullptr};
    context->CSSetUnorderedAccessViews(0,1,&nullUav,nullptr);
    context->CSSetShaderResources(0,3,nullView);
    context->CopyResource(staging,lightmapBuf);
    D3D11_MAPPED_SUBRESOURCE read{};
    if(FAILED(context->Map(staging,0,D3D11_MAP_READ,0,&read))){
        state="GPU readback failed: Standard fallback";
        return 0;
    }
    float rgb[LW*LH*4];
    std::memcpy(rgb,read.pData,sizeof rgb);
    context->Unmap(staging,0);
    // Keep the original palette picture at its full 256x240 pixel
    // resolution; only LIGHTING is interpolated from a 128x96 map.
    // Readback and CPU final composite are intentionally prototype-only.
    for(int y=CVIII_LIGHT_HUD;y<240;++y){
        float fy=((float)(y-CVIII_LIGHT_HUD)-.5f)*.5f;
        int iy=(int)std::floor(fy);
        float ty=fy-iy;
        int y0=std::max(0,std::min(LH-1,iy));
        int y1=std::max(0,std::min(LH-1,iy+1));
        for(int x=0;x<256;++x){
            float fx=((float)x-.5f)*.5f;
            int ix=(int)std::floor(fx);
            float tx=fx-ix;
            int x0=std::max(0,std::min(LW-1,ix));
            int x1=std::max(0,std::min(LW-1,ix+1));
            const float *a=&rgb[(y0*LW+x0)*4],
                        *b=&rgb[(y0*LW+x1)*4],
                        *c=&rgb[(y1*LW+x0)*4],
                        *d=&rgb[(y1*LW+x1)*4];
            float gain[3];
            for(int k=0;k<3;++k)
                gain[k]=((a[k]*(1-tx)+b[k]*tx)*(1-ty)+
                         (c[k]*(1-tx)+d[k]*tx)*ty);
            uint32_t p=pixels[y*256+x];
            float red=(float)channel((p>>16)&255,gain[0])*
                args.grade[0]*(1-.18f*args.grade[1]);
            float green=(float)channel((p>>8)&255,gain[1])*args.grade[0];
            float blue=(float)channel(p&255,gain[2])*
                args.grade[0]*(1+.18f*args.grade[1]);
            float luminosity=.2126f*red+.7152f*green+.0722f*blue;
            float saturation=args.grade[2];
            red=luminosity+(red-luminosity)*saturation;
            green=luminosity+(green-luminosity)*saturation;
            blue=luminosity+(blue-luminosity)*saturation;
            auto pack=[](float v)->uint32_t{
                return (uint32_t)clampf(std::floor(v+0.5f),0.f,255.f);
            };
            pixels[y*256+x]=(p&0xff000000u)|
                (pack(red)<<16)|(pack(green)<<8)|pack(blue);
        }
    }
    state="GPU D3D11 active: direct visibility + sampled 1 bounce";
    return 1;
}
} // namespace

extern "C" int cviii_gpu_rtgi_present(const CviiiLighting *settings,uint32_t *pixels,
                            uint32_t room,int camera,const int sx[CVIII_LIGHT_H],
                            const int sy[CVIII_LIGHT_H],uint64_t frame){
    return run(settings,pixels,room,camera,sx,sy,frame);
}
extern "C" const char *cviii_gpu_rtgi_status(void){return state;}
extern "C" void cviii_gpu_rtgi_reset(void){
    /* No temporal light accumulation: room changes/load cannot smear. */
}
