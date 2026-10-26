/* CVIII JP lighting workbench. Owner-private SDL2 overlay, no SDL_ttf,
 * ROM assets or additional redistributable DLLs. Included solely by the
 * pinned SDL patch. All geometry is in renderer logical 256x240 pixels. */
#ifndef CVIII_LIGHTING_PANEL_SDL_H
#define CVIII_LIGHTING_PANEL_SDL_H
#include "cviii_lighting_host.h"
#include <ctype.h>
#include <stdio.h>
#include <string.h>
enum { CVL_X=109, CVL_Y=3, CVL_W=144, CVL_H=234, CVL_ROWS=6 };
static int cvl_list_top, cvl_drag_property=-1, cvl_place_pending;
static int cvl_inside(int x,int y,int xx,int yy,int ww,int hh)
{ return x>=xx && x<xx+ww && y>=yy && y<yy+hh; }
static void cvl_fill(SDL_Renderer *r,int x,int y,int w,int h,
                     Uint8 cr,Uint8 cg,Uint8 cb,Uint8 ca)
{
    SDL_Rect b={x,y,w,h};
    SDL_SetRenderDrawColor(r,cr,cg,cb,ca);
    SDL_RenderFillRect(r,&b);
}
static void cvl_outline(SDL_Renderer *r,int x,int y,int w,int h,
                        Uint8 cr,Uint8 cg,Uint8 cb)
{
    SDL_Rect b={x,y,w,h};
    SDL_SetRenderDrawColor(r,cr,cg,cb,255);
    SDL_RenderDrawRect(r,&b);
}
static void cvl_text(SDL_Renderer *r,int x,int y,const char *s,
                     Uint8 cr,Uint8 cg,Uint8 cb)
{
    SDL_SetRenderDrawColor(r,cr,cg,cb,255);
    for(;*s && x<CVL_X+CVL_W-3;++s,x+=4){
        char c=(char)toupper((unsigned char)*s);
        const uint8_t *g=cyc_overlay_glyph(c);
        if(!g)continue;
        for(int yy=0;yy<5;++yy)
            for(int xx=0;xx<3;++xx)
                if(g[yy]&(4>>xx)){
                    SDL_Rect pixel={x+xx,y+yy,1,1};
                    SDL_RenderFillRect(r,&pixel);
                }
    }
}
static void cvl_button(SDL_Renderer *r,int x,int y,int w,const char *s,
                       int selected)
{
    cvl_fill(r,x,y,w,12,selected?24:39,selected?110:45,selected?140:57,244);
    cvl_outline(r,x,y,w,12,selected?87:89,selected?222:100,selected?245:120);
    cvl_text(r,x+5,y+4,s,237,244,250);
}
static int cvl_count(unsigned room)
{
    int n=0;
    const CviiiLighting *v=cviii_lighting_editor_model();
    for(int i=0;i<CVIII_LIGHT_MAX;++i)
        if(v->light[i].used && v->light[i].room==room)++n;
    return n;
}
static int cvl_slot(unsigned room,int ordinal)
{
    const CviiiLighting *v=cviii_lighting_editor_model();
    for(int i=0;i<CVIII_LIGHT_MAX;++i)
        if(v->light[i].used && v->light[i].room==room){
            if(ordinal==0)return i;
            --ordinal;
        }
    return -1;
}
static void cvl_slider(SDL_Renderer *r,int row,const char *name,int val,int lo,int hi,
                       Uint8 cr,Uint8 cg,Uint8 cb,int valid)
{
    char label[40];
    snprintf(label,sizeof label,"%s %d",name,val);
    int yy=row;
    cvl_text(r,CVL_X+7,yy,label,valid?197:106,valid?213:118,valid?221:128);
    cvl_fill(r,CVL_X+70,yy-1,65,7,33,41,52,255);
    cvl_outline(r,CVL_X+70,yy-1,65,7,69,81,93);
    if(hi>lo){
        int len=(val-lo)*63/(hi-lo);
        if(len<0)len=0;
        if(len>63)len=63;
        if(valid)cvl_fill(r,CVL_X+71,yy,1+len,5,cr,cg,cb,255);
        cvl_fill(r,CVL_X+70+len,yy-2,3,9,229,235,239,255);
    }
}
static void cviii_light_ui_draw(void)
{
    if(!cviii_lighting_editor_active() || !s_ren)return;
    SDL_SetRenderDrawBlendMode(s_ren,SDL_BLENDMODE_BLEND);
    const CviiiLighting *v=cviii_lighting_editor_model();
    unsigned room=cviii_lighting_editor_room();
    /* Clickable, high-contrast game-space handles remain available outside
       the dock. The list is always clickable even if the light is obscured. */
    for(int i=0;i<CVIII_LIGHT_MAX;++i){
        if(!v->light[i].used || v->light[i].room!=room)continue;
        int x=0,y=0;
        if(!cviii_lighting_editor_point(i,&x,&y))continue;
        int sel=i==v->selected;
        Uint8 rr=sel?255:112, gg=sel?228:219,bb=sel?100:242;
        cvl_fill(s_ren,x-3,y-3,7,7,16,23,30,217);
        cvl_outline(s_ren,x-5,y-5,11,11,rr,gg,bb);
        cvl_fill(s_ren,x-2,y-2,5,5,rr,gg,bb,255);
        SDL_SetRenderDrawColor(s_ren,rr,gg,bb,255);
        SDL_RenderDrawLine(s_ren,x-8,y,x-6,y);
        SDL_RenderDrawLine(s_ren,x+6,y,x+8,y);
        SDL_RenderDrawLine(s_ren,x,y-8,x,y-6);
        SDL_RenderDrawLine(s_ren,x,y+6,x,y+8);
    }
    cvl_fill(s_ren,CVL_X,CVL_Y,CVL_W,CVL_H,16,20,27,234);
    cvl_outline(s_ren,CVL_X,CVL_Y,CVL_W,CVL_H,81,101,121);
    cvl_fill(s_ren,CVL_X+1,CVL_Y+1,CVL_W-2,17,28,36,47,246);
    cvl_fill(s_ren,CVL_X+1,CVL_Y+18,CVL_W-2,2,57,193,218,255);
    cvl_text(s_ren,CVL_X+7,CVL_Y+7,"LIGHTING WORKBENCH",234,243,248);
    cvl_button(s_ren,CVL_X+5,24,40,cvl_place_pending?"PLACE":"ADD",cvl_place_pending);
    cvl_button(s_ren,CVL_X+48,24,43,"DELETE",0);
    cvl_button(s_ren,CVL_X+94,24,45,"CLOSE",0);
    cvl_text(s_ren,CVL_X+7,41,"SCENE LIGHTS",129,205,221);
    cvl_fill(s_ren,CVL_X+5,49,CVL_W-10,69,24,30,39,225);
    int count=cvl_count(room);
    if(cvl_list_top>count-CVL_ROWS)cvl_list_top=count>CVL_ROWS?count-CVL_ROWS:0;
    if(cvl_list_top<0)cvl_list_top=0;
    if(!count)cvl_text(s_ren,CVL_X+11,61,"NO LIGHTS - ADD",170,183,197);
    for(int row=0;row<CVL_ROWS;++row){
        int slot=cvl_slot(room,cvl_list_top+row);
        if(slot<0)break;
        const CviiiLight *l=&v->light[slot];
        int selected=slot==v->selected;
        int y=50+row*11;
        if(selected)cvl_fill(s_ren,CVL_X+7,y,130,10,35,93,114,245);
        char line[36];
        snprintf(line,sizeof line,"%02d  X%d Y%d",slot+1,l->x,l->y);
        cvl_text(s_ren,CVL_X+11,y+3,line,selected?248:181,selected?250:196,selected?251:205);
    }
    cvl_text(s_ren,CVL_X+7,122,"ENABLE",191,209,219);
    cvl_fill(s_ren,CVL_X+44,120,10,10,v->enabled?44:52,v->enabled?173:58,v->enabled?201:68,255);
    cvl_outline(s_ren,CVL_X+44,120,10,10,133,174,188);
    if(v->enabled)cvl_text(s_ren,CVL_X+47,123,"X",10,30,38);
    cvl_slider(s_ren,138,"AMB",v->ambient,35,100,77,191,210,1);
    int selected=v->selected>=0 && v->selected<CVIII_LIGHT_MAX &&
       v->light[v->selected].used && v->light[v->selected].room==room;
    const CviiiLight *l=selected?&v->light[v->selected]:NULL;
    cvl_slider(s_ren,156,"RADIUS",l?l->radius:56,12,160,82,194,213,selected);
    cvl_slider(s_ren,174,"POWER",l?l->energy:85,5,160,242,183,85,selected);
    cvl_slider(s_ren,192,"RED",l?l->red:255,0,255,220,86,77,selected);
    cvl_slider(s_ren,210,"GREEN",l?l->green:167,0,255,93,208,124,selected);
    cvl_slider(s_ren,227,"BLUE",l?l->blue:74,0,255,91,148,232,selected);
    SDL_SetRenderDrawBlendMode(s_ren,SDL_BLENDMODE_NONE);
}
/* Return: 0=game region, 1=panel action consumed, 2=changed presentation.
 * Called with already converted renderer logical coordinates. */
static int cviii_light_ui_mouse(int code,int x,int y)
{
    if(!cviii_lighting_editor_active())return 0;
    const CviiiLighting *v=cviii_lighting_editor_model();
    unsigned room=cviii_lighting_editor_room();
    if(code==4 && cvl_drag_property>=0){
        cvl_drag_property=-1;
        return 2;
    }
    if(!cvl_inside(x,y,CVL_X,CVL_Y,CVL_W,CVL_H)){
        if(code==2 && cvl_place_pending){
            if(cviii_lighting_editor_add(x,y)){
                cvl_place_pending=0;
                return 2;
            }
            return 1;
        }
        return 0;
    }
    if(code==13)return 1;
    if(code!=2 && code!=3 && code!=4)return 1;
    if(code==4)return 1;
    if(cvl_drag_property>=0 && code==3){
        int min=0,max=255;
        if(cvl_drag_property==1){min=35;max=100;}
        if(cvl_drag_property==2){min=12;max=160;}
        if(cvl_drag_property==3){min=5;max=160;}
        int k=x-(CVL_X+70);
        if(k<0)k=0;
        if(k>63)k=63;
        return cviii_lighting_editor_property(cvl_drag_property,min+(k*(max-min)+31)/63)?2:1;
    }
    if(code!=2)return 1;
    if(cvl_inside(x,y,CVL_X+5,24,40,12)){cvl_place_pending=1;return 1;}
    if(cvl_inside(x,y,CVL_X+48,24,43,12)){
        return cviii_lighting_editor_input(5,-1,-1)?2:1;
    }
    if(cvl_inside(x,y,CVL_X+94,24,45,12)){
        cvl_place_pending=0;
        return cviii_lighting_editor_input(1,-1,-1)?2:1;
    }
    if(cvl_inside(x,y,CVL_X+6,49,132,69)){
        int row=(y-50)/11;
        if(y>=50 && row>=0 && row<CVL_ROWS){
            int slot=cvl_slot(room,cvl_list_top+row);
            return cviii_lighting_editor_select(slot)?2:1;
        }
        return 1;
    }
    if(cvl_inside(x,y,CVL_X+44,120,10,10))
        return cviii_lighting_editor_property(0,!v->enabled)?2:1;
    for(int i=0;i<6;++i){
        int row=(int[]){138,156,174,192,210,227}[i];
        if(cvl_inside(x,y,CVL_X+67,row-4,72,13)){
            cvl_drag_property=i+1;
            return cviii_light_ui_mouse(3,x,y);
        }
    }
    return 1;
}
static int cviii_light_ui_wheel(int x,int y,int delta)
{
    if(!cviii_lighting_editor_active())return 0;
    if(!cvl_inside(x,y,CVL_X,CVL_Y,CVL_W,CVL_H))return 0;
    if(cvl_inside(x,y,CVL_X+5,49,CVL_W-10,69)){
        int count=cvl_count(cviii_lighting_editor_room());
        cvl_list_top+=delta>0?-1:1;
        if(cvl_list_top<0)cvl_list_top=0;
        if(cvl_list_top>count-CVL_ROWS)
            cvl_list_top=count>CVL_ROWS?count-CVL_ROWS:0;
    }
    return 1;
}
#endif
