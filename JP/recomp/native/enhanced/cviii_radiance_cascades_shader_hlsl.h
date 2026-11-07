/* CVIII Radiance Cascades 2D -- independent D3D11 CS5.0 shader source.
 * Each level has exactly 6144 probe-rays: 32x24x8, 16x12x32,
 * 8x6x128, 4x3x512. The radial intervals scale by four.
 * Merges from the coarsest level down: local radiance +
 * transmittance * bilinear far-probe radiance (4 angular children).
 * Input materials are ONLY the editor-authored wall rectangles.
 */
#ifndef CVIII_RADIANCE_CASCADES_SHADER_H
#define CVIII_RADIANCE_CASCADES_SHADER_H
static const char cviii_rc_hlsl[] = R"CVIIIRC(
struct W {float4 bounds;float4 attrs;float4 albedo;};
StructuredBuffer<W> walls : register(t0);
StructuredBuffer<int2> scanlines : register(t1);
StructuredBuffer<float4> farther : register(t2);
RWStructuredBuffer<float4> cascadeOut : register(u0);
cbuffer RCGlobals : register(b0){
    uint level;
    uint wallsCount;
    uint levelsCount;
    uint rayCount;
};
static const float TAU=6.283185307179586;
uint rays(uint levelIdx){return 8u << (levelIdx*2u);}
uint cols(uint levelIdx){return 32u >> levelIdx;}
uint rows(uint levelIdx){return 24u >> levelIdx;}
float2 origin(uint x,uint y,uint l){
    uint step=1u<<l;
    uint scanRow=min(95u,(y*step*4u)+(step*2u));
    int2 sampleScan=scanlines[scanRow];
    return float2(sampleScan.x+(x+.5)*(8u<<l),sampleScan.y);
}
bool hitBox(float2 p,float2 dir,float2 boundsMin,float2 boundsMax,
            out float hitT,out float2 norm){
    float enter=-100000,exit=100000;
    float2 normal=0;
    [unroll] for(int d=0;d<2;++d){
        float originCoord=d==0?p.x:p.y;
        float delta=d==0?dir.x:dir.y;
        float lo=d==0?boundsMin.x:boundsMin.y;
        float hi=d==0?boundsMax.x:boundsMax.y;
        if(abs(delta)<0.000001){
            if(originCoord<lo || originCoord>hi){hitT=0;norm=0;return false;}
        }else{
            float t0=(lo-originCoord)/delta;
            float t1=(hi-originCoord)/delta;
            float side=-1.0;
            if(t0>t1){float temp=t0;t0=t1;t1=temp;side=1;}
            if(t0>enter){
                enter=t0;
                normal=d==0?float2(side,0):float2(0,side);
            }
            exit=min(exit,t1);
            if(exit<enter){hitT=0;norm=0;return false;}
        }
    }
    if(exit<=0){hitT=0;norm=0;return false;}
    hitT=max(0,enter);norm=normal;
    return true;
}
float4 trace(float2 p,float2 dir,float begin,float end){
    float nearest=end+.01;
    float4 result=float4(0,0,0,1);
    [loop] for(uint i=0;i<wallsCount;++i){
        W w=walls[i];
        if(w.attrs.x<=.001)continue;
        float distance;float2 normal;
        if(!hitBox(p,dir,w.bounds.xy,w.bounds.xy+w.bounds.zw,
                   distance,normal))continue;
        if(distance<begin || distance>=nearest || distance>end)continue;
        nearest=distance;
        // Only the illuminated wall face emits bounce: the back face
        // should block light, but must not glow through masonry.
        float litSide=dot(normal,p-w.attrs.zw)>0?1:0;
        result=float4(w.albedo.rgb*litSide*w.attrs.x,1-w.attrs.x);
    }
    return result;
}
float4 sampleFar(int px,int py,uint direction){
    uint gx=cols(level+1),gy=rows(level+1),a=rays(level+1);
    px=clamp(px,0,(int)gx-1);
    py=clamp(py,0,(int)gy-1);
    return farther[((uint)py*gx+(uint)px)*a+direction];
}
float4 bilinearFar(float2 at,uint direction){
    // Coordinates are in game-native pixels. Coarser probes are
    // spatially interpolated, angularly supersampled four times.
    float spacing=float(8u<<(level+1u));
    float2 uv=(at-float2(scanlines[0].x,scanlines[0].y))/spacing-.5;
    // World x origin can vary with scrolling per scanline. Use the
    // local coarser scanline origin to avoid camera-fixed GI patterns.
    uint yProbe=(uint)clamp(int(floor(uv.y+.5)),0,(int)rows(level+1)-1);
    uint cy=min(95u,yProbe*(1u<<(level+1u))*4u+2u*(1u<<(level+1u)));
    uv.x=(at.x-scanlines[cy].x)/spacing-.5;
    int2 p=int2(floor(uv));
    float2 f=saturate(frac(uv));
    float4 a=sampleFar(p.x,p.y,direction);
    float4 b=sampleFar(p.x+1,p.y,direction);
    float4 c=sampleFar(p.x,p.y+1,direction);
    float4 d=sampleFar(p.x+1,p.y+1,direction);
    return lerp(lerp(a,b,f.x),lerp(c,d,f.x),f.y);
}
[numthreads(64,1,1)]
void cascadeMain(uint3 id:SV_DispatchThreadID){
    if(id.x>=6144u)return;
    uint angleCount=rays(level);
    uint probe=id.x/angleCount;
    uint direction=id.x%angleCount;
    uint w=cols(level);
    uint probeX=probe%w,probeY=probe/w;
    float2 p=origin(probeX,probeY,level);
    float angle=TAU*(direction+.5)/angleCount;
    float2 ray=float2(cos(angle),sin(angle));
    // Distinct non-overlapping intervals 0..8, 8..32, 32..128, 128..512.
    float start=(pow(4.0,level)-1.0)*8.0/3.0;
    float end=(pow(4.0,level+1u)-1.0)*8.0/3.0;
    float4 nearRay=trace(p,ray,start,end);
    if(level+1u<levelsCount){
        float4 farRay=0;
        [unroll] for(uint angular=0;angular<4u;++angular){
            uint child=direction*4u+angular;
            farRay+=bilinearFar(p,child)*.25;
        }
        nearRay=float4(nearRay.rgb+nearRay.a*farRay.rgb,
                       nearRay.a*farRay.a);
    }
    cascadeOut[id.x]=nearRay;
}
StructuredBuffer<float4> inner : register(t3);
RWStructuredBuffer<float4> sceneLight : register(u1);
[numthreads(8,8,1)]
void resolveMain(uint3 id:SV_DispatchThreadID){
    if(id.x>=128u || id.y>=96u)return;
    // Probe-zero spacing is 8 NES pixels (4 low-res lightmap pixels).
    float2 uv=(float2(id.xy)*2.0+1.0)/8.0-.5;
    int2 p=int2(floor(uv));float2 f=saturate(frac(uv));
    float3 irradiance=0;
    [unroll] for(uint ray=0;ray<8u;++ray){
        int2 p00=clamp(p,int2(0,0),int2(31,23));
        int2 p10=clamp(p+int2(1,0),int2(0,0),int2(31,23));
        int2 p01=clamp(p+int2(0,1),int2(0,0),int2(31,23));
        int2 p11=clamp(p+int2(1,1),int2(0,0),int2(31,23));
        float3 a=inner[(p00.y*32+p00.x)*8+ray].rgb;
        float3 b=inner[(p10.y*32+p10.x)*8+ray].rgb;
        float3 c=inner[(p01.y*32+p01.x)*8+ray].rgb;
        float3 d=inner[(p11.y*32+p11.x)*8+ray].rgb;
        irradiance+=lerp(lerp(a,b,f.x),lerp(c,d,f.x),f.y);
    }
    // Probe integration adds bounced light, not a replacement for the
    // independent existing direct/ambient pass.
    irradiance*=.125;
    uint at=id.y*128u+id.x;
    sceneLight[at]=min(float4(sceneLight[at].rgb+
                                irradiance*1.25,1),16.0);
}
)CVIIIRC";
#endif
