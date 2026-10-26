/* One canonical embedded HLSL source for runtime D3D11 and ROM-free
 * shader compiler smoke on Windows. Keep shader compilation independent
 * from the real original-game/SDL2 executable. */
#ifndef CVIII_GPU_SHADER_HLSL_H
#define CVIII_GPU_SHADER_HLSL_H
static const char cviii_gpu_hlsl[] =R"CVIIIRTX(
struct L {float4 pos;float4 col;float4 dir;float4 anim;};
struct W {float4 bounds;float4 attr;float4 alb;};
StructuredBuffer<L> light : register(t0);
StructuredBuffer<W> wall : register(t1);
StructuredBuffer<int2> scan : register(t2);
RWStructuredBuffer<float4> outLight : register(u0);
cbuffer Globals : register(b0) {
    uint nlight,nwall,frame,pad;
    float4 ambientSky;
    float4 skyColor;
    float4 grade;
}
static const float PI2=6.283185307179586;
bool segmentBox(float2 a,float2 b,float4 r){
    float2 d=b-a;
    float lo=0,hi=1;
    [unroll] for(int axis=0;axis<2;++axis){
        float delta=axis==0?d.x:d.y, origin=axis==0?a.x:a.y;
        float vmin=axis==0?r.x:r.y;
        float vmax=axis==0?r.x+r.z:r.y+r.w;
        if(abs(delta)<0.00001){
            if(origin<vmin || origin>vmax)return false;
        }else{
            float t0=(vmin-origin)/delta,t1=(vmax-origin)/delta;
            if(t0>t1){float temp=t0;t0=t1;t1=temp;}
            lo=max(lo,t0);hi=min(hi,t1);
            if(lo>hi)return false;
        }
    }
    return lo<0.999 && hi>0.001;
}
float blocked(float2 a,float2 b,int skip){
    float transmit=1;
    [loop] for(uint i=0;i<nwall;++i){
        if((int)i==skip)continue;
        W m=wall[i];
        if(m.attr.x<=0)continue;
        if(a.x>=m.bounds.x && a.x<=m.bounds.x+m.bounds.z &&
           a.y>=m.bounds.y && a.y<=m.bounds.y+m.bounds.w)continue;
        float spread=m.attr.y;
        float mask=0;
        [unroll] for(int y=-1;y<=1;++y){
            [unroll] for(int x=-1;x<=1;++x){
                int weight=(x==0?2:1)*(y==0?2:1);
                float2 pos=a+float2(x,y)*spread;
                if(segmentBox(pos,b,m.bounds))mask+=weight;
            }
        }
        transmit*=1-(m.attr.x*mask/16.0);
        if(transmit<0.008)return 0;
    }
    return transmit;
}
float waveform(L l,uint id){
    float pace=l.anim.y>0?l.anim.y:1.0;
    float depth=l.anim.z>0?l.anim.z:1.0;
    float t=(frame%216000)/60.0*pace,phase=id*1.6180339;
    float warm=(l.col.x>l.col.z && l.col.x>=l.col.y)?1:0;
    float slow=.018*sin(PI2*.73*t+phase)+.012*sin(PI2*1.71*t+phase*2.3);
    float fast=l.pos.w>=100?.009*sin(PI2*10.2*t+phase):0;
    float v=0;
    int mode=(int)l.anim.x;
    if(mode==0)v=warm*(slow+fast);
    if(mode==2)v=warm*(slow+fast)*2.7;
    if(mode==3)v=.115*sin(PI2*.43*t+phase)+.035*sin(PI2*.97*t+phase*.61);
    if(mode==4){
        float f=.5+.5*sin(PI2*.67*t+phase);
        v=.018*sin(PI2*2.1*t+phase*2)-.16*f*f*f*f;
    }
    return clamp(1+v*depth,.7,1.35);
}
float falloff(L l,float2 pixel,float modulate){
    float2 d=pixel-l.pos.xy;
    float radius=l.pos.z*(1+.16*(modulate-1));
    float edge;
    if(l.col.w<.5){
        edge=1-length(d)/radius;
    }else{
        float2 axis=l.dir.xy;
        float along=dot(d,axis);
        float across=abs(dot(d,float2(-axis.y,axis.x)));
        if(along<0 || along>=radius)return 0;
        float halfWidth=l.col.w<1.5?2+along*l.dir.z:.5*l.dir.w;
        edge=(1-across/max(halfWidth,.5))*(1-along/radius);
    }
    float t=saturate(edge);
    return t*t*(3-2*t);
}
float3 bounce(float2 pixel){
    float3 bounced=0;
    [loop] for(uint i=0;i<nwall;++i){
        W surface=wall[i];
        float2 c=surface.attr.zw;
        float2 normal=c-(surface.bounds.xy+.5*surface.bounds.zw);
        float2 displacement=pixel-c;
        if(dot(normal,displacement)<=0)continue;
        float distanceTo=length(displacement);
        if(distanceTo>128 || distanceTo<1)continue;
        float attenuation=saturate(1-distanceTo/128);
        float visible=blocked(c,pixel,(int)i);
        bounced+=surface.alb.rgb*attenuation*attenuation*visible;
    }
    return bounced;
}
[numthreads(8,8,1)]
void main(uint3 id:SV_DispatchThreadID){
    if(id.x>=128 || id.y>=96)return;
    int2 sc=scan[id.y];
    float2 pixel=float2(sc.x+id.x*2+1,sc.y);
    float vertical=id.y/95.0;
    float hemi=skyColor.w==0?.7:(skyColor.w<0?
        1-.75*vertical:.25+.75*vertical);
    float3 color=ambientSky.xyz +
        (ambientSky.w*.014*hemi)*skyColor.xyz;
    [loop] for(uint i=0;i<nlight;++i){
        L l=light[i];
        float flicker=waveform(l,i);
        float atten=falloff(l,pixel,flicker);
        if(atten>0){
            float power=flicker*l.pos.w*.014*atten;
            color+=l.col.rgb*power*blocked(l.pos.xy,pixel,-1);
        }
    }
    if(pad==0u)color+=bounce(pixel); // RC computes its own indirect term
    outLight[id.y*128+id.x]=float4(min(color,16),1);
}
)CVIIIRTX";
#endif
