/* Optional real ReShade add-on for CVIII Enhanced Lighting.
 * ReShade itself (not our native SDL2 GUI) owns the overlay/context.
 * Win64, ReShade full-add-on runtime. Do not vendor or bundle ReShade.
 */
#include <Windows.h>
#define IMGUI_DISABLE_INCLUDE_IMCONFIG_H
#include <imgui.h>
#include <reshade.hpp>
#include <cstdio>
#include <cstring>
#include "cviii_lighting.h"

namespace {
struct Bridge {
    const CviiiLighting *(*model)()=nullptr;
    unsigned (*room)()=nullptr;
    int (*session)(int)=nullptr;
    int (*select)(int)=nullptr;
    int (*add)(int,int)=nullptr;
    int (*place_window)(int,int)=nullptr;
    int (*place_kit_window)(int,int,int,int)=nullptr;
    int (*apply_builtin)(int,int,int)=nullptr;
    int (*apply_kit)(int,int,int)=nullptr;
    int (*capture_kit)(int,const char*)=nullptr;
    int (*sky)(int,int)=nullptr;
    unsigned (*raw_room)()=nullptr;
    int (*alias)(unsigned)=nullptr;
    int (*global_capture)(int,const char*)=nullptr;
    int (*global_link)(int,int)=nullptr;
    int (*global_property)(int,int,int)=nullptr;
    int (*mask_add)(int,int,int,int)=nullptr;
    int (*mask_property)(int,int,int)=nullptr;
    int (*grade)(int,int)=nullptr;
    int (*undo)()=nullptr;
    int (*redo)()=nullptr;
    int (*kit_manage)(int,int,int,const char*)=nullptr;
    int (*builtin_count)()=nullptr;
    const char *(*builtin_name)(int)=nullptr;
    int (*event)(int,int,int)=nullptr;
    int (*prop)(int,int)=nullptr;
    int (*copy)()=nullptr;
    int (*paste)()=nullptr;
    int (*duplicate)()=nullptr;
    int (*name)(const char*)=nullptr;
    int (*group)(const char*)=nullptr;
    int (*scene)(int,int)=nullptr;
    void (*save)()=nullptr;
} bridge;
bool external_open=false;
bool placement_pending=false;
int pending_kit_kind=-1,pending_kit_id=-1;
char kit_name[CVIII_LIGHT_NAME_CAP]="My Lighting Rig";
int kit_slot=0,global_style_slot=0,mask_slot=0;
char global_name[CVIII_LIGHT_NAME_CAP]="Global Torch";
unsigned alias_target=0,last_raw=0;
unsigned long long presented=0,last_editor_draw=0;
char search[64]={};

template<typename T> T game_export(HMODULE exe,const char *name){
    return reinterpret_cast<T>(GetProcAddress(exe,name));
}
bool bind_game(){
    if(bridge.model)return true;
    HMODULE exe=GetModuleHandleW(nullptr);
    if(!exe)return false;
    Bridge b{};
    b.model=game_export<decltype(b.model)>(exe,"cviii_lighting_editor_model");
    b.room=game_export<decltype(b.room)>(exe,"cviii_lighting_editor_room");
    b.session=game_export<decltype(b.session)>(exe,"cviii_lighting_editor_external_session");
    b.select=game_export<decltype(b.select)>(exe,"cviii_lighting_editor_select");
    b.add=game_export<decltype(b.add)>(exe,"cviii_lighting_editor_add");
    b.place_window=game_export<decltype(b.place_window)>(exe,"cviii_light_place_window");
    b.place_kit_window=game_export<decltype(b.place_kit_window)>(exe,"cviii_light_place_kit_window");
    b.apply_builtin=game_export<decltype(b.apply_builtin)>(exe,"cviii_lighting_editor_apply_builtin");
    b.apply_kit=game_export<decltype(b.apply_kit)>(exe,"cviii_lighting_editor_apply_kit");
    b.capture_kit=game_export<decltype(b.capture_kit)>(exe,"cviii_lighting_editor_capture_kit");
    b.sky=game_export<decltype(b.sky)>(exe,"cviii_lighting_editor_sky");
    b.raw_room=game_export<decltype(b.raw_room)>(exe,"cviii_lighting_editor_raw_room");
    b.alias=game_export<decltype(b.alias)>(exe,"cviii_lighting_editor_alias");
    b.global_capture=game_export<decltype(b.global_capture)>(exe,"cviii_lighting_editor_global_capture");
    b.global_link=game_export<decltype(b.global_link)>(exe,"cviii_lighting_editor_global_link");
    b.global_property=game_export<decltype(b.global_property)>(exe,"cviii_lighting_editor_global_property");
    b.mask_add=game_export<decltype(b.mask_add)>(exe,"cviii_lighting_editor_mask_add");
    b.mask_property=game_export<decltype(b.mask_property)>(exe,"cviii_lighting_editor_mask_property");
    b.grade=game_export<decltype(b.grade)>(exe,"cviii_lighting_editor_grade");
    b.undo=game_export<decltype(b.undo)>(exe,"cviii_lighting_editor_undo");
    b.redo=game_export<decltype(b.redo)>(exe,"cviii_lighting_editor_redo");
    b.kit_manage=game_export<decltype(b.kit_manage)>(exe,"cviii_lighting_editor_kit_manage");
    b.builtin_count=game_export<decltype(b.builtin_count)>(exe,"cviii_lighting_editor_builtin_count");
    b.builtin_name=game_export<decltype(b.builtin_name)>(exe,"cviii_lighting_editor_builtin_name");
    b.event=game_export<decltype(b.event)>(exe,"cviii_lighting_editor_input");
    b.prop=game_export<decltype(b.prop)>(exe,"cviii_lighting_editor_property");
    b.copy=game_export<decltype(b.copy)>(exe,"cviii_lighting_editor_copy");
    b.paste=game_export<decltype(b.paste)>(exe,"cviii_lighting_editor_paste");
    b.duplicate=game_export<decltype(b.duplicate)>(exe,"cviii_lighting_editor_duplicate");
    b.name=game_export<decltype(b.name)>(exe,"cviii_lighting_editor_name");
    b.group=game_export<decltype(b.group)>(exe,"cviii_lighting_editor_group");
    b.scene=game_export<decltype(b.scene)>(exe,"cviii_lighting_editor_scene");
    b.save=game_export<decltype(b.save)>(exe,"cviii_light_force_save");
    if(!b.model || !b.room || !b.session || !b.select || !b.add ||
       !b.place_window || !b.place_kit_window || !b.apply_builtin ||
       !b.apply_kit || !b.capture_kit || !b.sky ||
       !b.raw_room || !b.alias || !b.global_capture || !b.global_link ||
       !b.global_property || !b.mask_add || !b.mask_property || !b.grade ||
       !b.undo || !b.redo || !b.kit_manage ||
       !b.builtin_count || !b.builtin_name ||
       !b.event || !b.prop ||
       !b.copy || !b.paste || !b.duplicate || !b.name || !b.group ||
       !b.scene || !b.save)return false;
    bridge=b;
    return true;
}
void changed(int result){if(result)bridge.save();}
void end_session(){
    if(external_open && bridge.session){
        bridge.session(0);
        if(bridge.save)bridge.save();
    }
    external_open=false;
    placement_pending=false;
    pending_kit_kind=-1;
}
void on_present(reshade::api::effect_runtime *){
    ++presented;
    if(external_open && presented-last_editor_draw>2)end_session();
}
void on_overlay(reshade::api::effect_runtime *){
    if(!bind_game()){
        ImGui::TextDisabled("CVIII Enhanced lighting bridge not found.");
        ImGui::TextWrapped("Use a Windows lighting-preview build with "
                           "the exported ReShade host bridge.");
        return;
    }
    /* Refresh the editor session every visible overlay frame. The NES
     * power/load callbacks can end it without destroying the ReShade UI. */
    if(!bridge.session(1)){
        external_open=false;
        ImGui::TextDisabled("Lighting editing requires Enhanced gameplay.");
        return;
    }
    external_open=true;
    last_editor_draw=presented;

    const CviiiLighting *s=bridge.model();
    const unsigned room=bridge.room();
    bool enabled=s->enabled!=0;
    if(ImGui::Checkbox("Enable Lighting",&enabled))
        changed(bridge.prop(0,enabled?1:0));
    ImGui::SameLine();
    ImGui::TextDisabled("Scene %08X",room);
    if(ImGui::SmallButton("Undo"))changed(bridge.undo());
    ImGui::SameLine();
    if(ImGui::SmallButton("Redo"))changed(bridge.redo());
    ImGui::SameLine();
    ImGui::TextDisabled("Undo/Redo affect lighting only");
    ImGui::InputTextWithHint("##filter","Filter lights and groups...",search,sizeof search);
    if(ImGui::Button(placement_pending?"CLICK ON LEVEL...":"Add Light: Click Level")){
        placement_pending=true;pending_kit_kind=-1;pending_kit_id=-1;
    }
    ImGui::SameLine();
    if(ImGui::Button("Add at Center"))changed(bridge.add(128,120));
    ImGui::SameLine();
    if(ImGui::Button("Copy"))(void)bridge.copy();
    ImGui::SameLine();
    if(ImGui::Button("Paste in Scene"))changed(bridge.paste());
    ImGui::SameLine();
    if(ImGui::Button("Duplicate"))changed(bridge.duplicate());
    ImGui::SameLine();
    if(ImGui::Button("Delete Selected")){
        int i=s->selected;
        if(i>=0 && i<CVIII_LIGHT_MAX && s->light[i].used){
            changed(bridge.event(5,-1,-1));
        }
    }

    if(ImGui::CollapsingHeader("Global Lighting Library",ImGuiTreeNodeFlags_DefaultOpen)){
        ImGui::TextDisabled("Reusable groups. Place in any room.");
        for(int i=0;i<bridge.builtin_count();++i){
            ImGui::PushID(i);
            ImGui::TextUnformatted(bridge.builtin_name(i));
            ImGui::SameLine(190);
            if(ImGui::SmallButton("Apply here"))changed(bridge.apply_builtin(i,-1,-1));
            ImGui::SameLine();
            if(ImGui::SmallButton("Place...")){
                placement_pending=true;pending_kit_kind=0;pending_kit_id=i;
            }
            ImGui::PopID();
        }
        ImGui::InputText("Kit Name",kit_name,sizeof kit_name);
        ImGui::SliderInt("Kit Slot",&kit_slot,0,CVIII_KIT_MAX-1);
        if(ImGui::Button("Save selected group as global kit"))
            changed(bridge.capture_kit(kit_slot,kit_name));
        if(s->kits[kit_slot].used){
            if(ImGui::SmallButton("Rename Saved Kit"))
                changed(bridge.kit_manage(1,kit_slot,-1,kit_name));
            ImGui::SameLine();
            if(ImGui::SmallButton("Clone to Empty Slot")){
                for(int i=0;i<CVIII_KIT_MAX;++i)
                    if(!s->kits[i].used){
                        changed(bridge.kit_manage(2,kit_slot,i,nullptr));
                        kit_slot=i;break;
                    }
            }
            ImGui::SameLine();
            if(ImGui::SmallButton("Delete Saved Kit"))
                changed(bridge.kit_manage(3,kit_slot,-1,nullptr));
        }
        for(int i=0;i<CVIII_KIT_MAX;++i){
            if(!s->kits[i].used)continue;
            ImGui::PushID(500+i);
            ImGui::Text("%02d. %s (%d lights)",i+1,s->kits[i].name,s->kits[i].count);
            ImGui::SameLine(210);
            if(ImGui::SmallButton("Apply"))changed(bridge.apply_kit(i,-1,-1));
            ImGui::SameLine();
            if(ImGui::SmallButton("Place")){
                placement_pending=true;pending_kit_kind=1;pending_kit_id=i;
            }
            ImGui::PopID();
        }
    }
    if(placement_pending){
        ImGui::TextDisabled("Click the exposed scene to place the selected rig.");
        if(ImGui::SmallButton("Cancel placement")){
            placement_pending=false;pending_kit_kind=-1;pending_kit_id=-1;
        }
    }
    ImGui::SeparatorText("Scene Lights");
    if(ImGui::BeginChild("##list",ImVec2(0,175),ImGuiChildFlags_Borders)){
        for(int i=0;i<CVIII_LIGHT_MAX;++i){
            const CviiiLight &l=s->light[i];
            if(!l.used || l.room!=room)continue;
            if(search[0] &&
               !std::strstr(l.name,search) && !std::strstr(l.group,search))
                continue;
            ImGui::PushID(i);
            char title[160];
            std::snprintf(title,sizeof title,"%s  /  %s  [%d,%d]",
                l.name[0]?l.name:"Unnamed",l.group[0]?l.group:"Ungrouped",
                l.x,l.y);
            if(ImGui::Selectable(title,s->selected==i))bridge.select(i);
            ImGui::PopID();
        }
    }
    ImGui::EndChild();
    if(s->selected>=0 && s->selected<CVIII_LIGHT_MAX &&
       s->light[s->selected].used && s->light[s->selected].room==room){
        const CviiiLight &l=s->light[s->selected];
        ImGui::SeparatorText("Emitter");
        char label[CVIII_LIGHT_NAME_CAP],group[CVIII_LIGHT_GROUP_CAP];
        std::snprintf(label,sizeof label,"%s",l.name);
        std::snprintf(group,sizeof group,"%s",l.group);
        if(ImGui::InputText("Name",label,sizeof label))changed(bridge.name(label));
        if(ImGui::InputText("Group",group,sizeof group))changed(bridge.group(group));
        int type=l.shape;
        if(ImGui::Combo("Shape",&type,"Radial\0Cone\0Shaft\0"))
            changed(bridge.prop(7,type));
        int posx=l.x,posy=l.y;
        if(ImGui::InputInt("World X",&posx,1,16))changed(bridge.prop(13,posx));
        if(ImGui::InputInt("World Y",&posy,1,8))changed(bridge.prop(14,posy));
        int radius=l.radius,energy=l.energy;
        if(ImGui::SliderInt("Range",&radius,12,160))changed(bridge.prop(2,radius));
        if(ImGui::SliderInt("Intensity",&energy,5,160))changed(bridge.prop(3,energy));
        if(type!=CVIII_SHAPE_RADIAL){
            int angle=l.angle;
            if(ImGui::SliderInt("Direction",&angle,0,359))changed(bridge.prop(8,angle));
            int param=type==CVIII_SHAPE_CONE?(l.spread?l.spread:30):(l.width?l.width:32);
            if(ImGui::SliderInt(type==CVIII_SHAPE_CONE?"Cone Angle":"Shaft Width",
                                &param,type==CVIII_SHAPE_CONE?5:4,
                                type==CVIII_SHAPE_CONE?85:160))
                changed(bridge.prop(type==CVIII_SHAPE_CONE?9:10,param));
        }
        float rgb[3]={l.red/255.f,l.green/255.f,l.blue/255.f};
        if(ImGui::ColorEdit3("Emitter Color",rgb,ImGuiColorEditFlags_PickerHueWheel)){
            for(int k=0;k<3;++k)
                changed(bridge.prop(4+k,(int)(rgb[k]*255.f+0.5f)));
        }
        int flicker=l.flicker;
        if(ImGui::Combo("Flicker",&flicker,"Subtle\0Steady\0Torch\0"))
            changed(bridge.prop(12,flicker));
        bool muted=l.muted!=0;
        if(ImGui::Checkbox("Mute emitter",&muted))
            changed(bridge.prop(11,muted?1:0));
    }
    ImGui::SeparatorText("Scene Ambient");
    int lvl=s->ambient,tint[3]={255,255,255};
    /* ReShade DLL only reads the C ABI snapshot; it never links directly
     * against the original C11 executable's internal helper objects. */
    for(int i=0;i<CVIII_SCENE_AMBIENT_MAX;++i){
        const CviiiSceneAmbient &a=s->scenes[i];
        if(!a.used || a.room!=room)continue;
        lvl=a.level;tint[0]=a.red;tint[1]=a.green;tint[2]=a.blue;
        break;
    }
    if(ImGui::SliderInt("Ambient Strength",&lvl,0,100,"%d%%"))
        changed(bridge.scene(0,lvl));
    float c[3]={tint[0]/255.f,tint[1]/255.f,tint[2]/255.f};
    if(ImGui::ColorEdit3("Ambient Color",c,ImGuiColorEditFlags_PickerHueWheel))
        for(int k=0;k<3;++k)
            changed(bridge.scene(k+1,(int)(c[k]*255.f+0.5f)));
    if(ImGui::CollapsingHeader("Global Styles / Linked Groups",ImGuiTreeNodeFlags_DefaultOpen)){
        ImGui::TextWrapped("Capture a light as a shared style; link any placed "
                           "light or named group to it across all rooms.");
        ImGui::InputText("Global Name",global_name,sizeof global_name);
        ImGui::SliderInt("Global Slot",&global_style_slot,0,CVIII_GLOBAL_STYLE_MAX-1);
        if(ImGui::Button("Capture Selected"))changed(bridge.global_capture(global_style_slot,global_name));
        ImGui::SameLine();
        if(ImGui::Button("Link Selected"))changed(bridge.global_link(global_style_slot,0));
        ImGui::SameLine();
        if(ImGui::Button("Link Group"))changed(bridge.global_link(global_style_slot,1));
        if(ImGui::Button("Unlink Selected"))changed(bridge.global_link(-1,0));
        const CviiiGlobalStyle &style=s->styles[global_style_slot];
        if(style.used){
            ImGui::Text("Shared style: %s",style.name);
            int radius=style.light.radius,energy=style.light.energy;
            if(ImGui::SliderInt("Global Range",&radius,12,160))
                changed(bridge.global_property(global_style_slot,2,radius));
            if(ImGui::SliderInt("Global Power",&energy,5,160))
                changed(bridge.global_property(global_style_slot,3,energy));
            float color[3]={style.light.red/255.f,style.light.green/255.f,style.light.blue/255.f};
            if(ImGui::ColorEdit3("Global RGB",color,ImGuiColorEditFlags_PickerHueWheel))
                for(int k=0;k<3;++k)
                    changed(bridge.global_property(global_style_slot,4+k,
                      (int)(color[k]*255.f+0.5f)));
        }
        for(int i=0;i<CVIII_GLOBAL_STYLE_MAX;++i)if(s->styles[i].used){
            ImGui::PushID(i+800);
            if(ImGui::Selectable(s->styles[i].name,i==global_style_slot))global_style_slot=i;
            ImGui::PopID();
        }
    }
    if(ImGui::CollapsingHeader("Masks / Soft Occlusion")){
        const int selected=s->selected;
        if(selected>=0 && selected<CVIII_LIGHT_MAX &&
           s->light[selected].used && s->light[selected].room==room){
            if(ImGui::Button("Add Wall Mask Near Selected Light")){
                const CviiiLight &l=s->light[selected];
                int y=l.y>25?l.y-15:l.y;
                changed(bridge.mask_add(l.x+18,y,10,30)>=0);
            }
        }
        for(int i=0;i<CVIII_OCCLUDER_MAX;++i){
            if(!s->masks[i].used || s->masks[i].room!=room)continue;
            char title[32];std::snprintf(title,sizeof title,"Mask %02d",i+1);
            if(ImGui::Selectable(title,i==mask_slot))mask_slot=i;
        }
        if(mask_slot>=0 && mask_slot<CVIII_OCCLUDER_MAX &&
           s->masks[mask_slot].used && s->masks[mask_slot].room==room){
            const CviiiOccluder &mask=s->masks[mask_slot];
            int x=mask.x,y=mask.y,w=mask.w,h=mask.h,alpha=mask.opacity,soft=mask.softness;
            if(ImGui::InputInt("X##mask",&x))changed(bridge.mask_property(mask_slot,1,x));
            if(ImGui::InputInt("Y##mask",&y))changed(bridge.mask_property(mask_slot,2,y));
            if(ImGui::SliderInt("Width##mask",&w,1,160))
                changed(bridge.mask_property(mask_slot,3,w));
            if(ImGui::SliderInt("Height##mask",&h,1,160))
                changed(bridge.mask_property(mask_slot,4,h));
            if(ImGui::SliderInt("Shadow Opacity",&alpha,0,100))
                changed(bridge.mask_property(mask_slot,5,alpha));
            if(ImGui::SliderInt("Penumbra Softness",&soft,0,16))
                changed(bridge.mask_property(mask_slot,6,soft));
            if(ImGui::Button("Remove Mask"))changed(bridge.mask_property(mask_slot,0,0));
        }
        ImGui::TextDisabled("Manually authored 2D masks; no tile collision inference.");
    }
    if(ImGui::CollapsingHeader("Exposure / White Balance")){
        int ev=0,temp=0,sat=100;
        for(int i=0;i<CVIII_SCENE_AMBIENT_MAX;++i){
            const CviiiSceneAmbient &a=s->scenes[i];
            if(!a.used || a.room!=room || !a.graded)continue;
            ev=a.exposure;temp=a.temperature;sat=a.saturation;
            break;
        }
        if(ImGui::SliderInt("Exposure (EV x100)",&ev,-200,200))
            changed(bridge.grade(0,ev));
        if(ImGui::SliderInt("White Balance",&temp,-100,100))
            changed(bridge.grade(1,temp));
        if(ImGui::SliderInt("Saturation",&sat,0,200))
            changed(bridge.grade(2,sat));
        if(ImGui::Button("Reset Grade")){
            changed(bridge.grade(0,0));changed(bridge.grade(1,0));
            changed(bridge.grade(2,100));
        }
    }
    if(ImGui::CollapsingHeader("Persistent Scene Identity")){
        unsigned raw=bridge.raw_room();
        if(raw!=last_raw){last_raw=raw;alias_target=room;}
        ImGui::Text("Raw %08X   Linked Scene %08X",raw,room);
        ImGui::TextWrapped("If revisiting a room produces a different raw key, "
           "enter the original saved scene ID to restore the same lights.");
        ImGui::InputScalar("Saved Scene ID",ImGuiDataType_U32,&alias_target,
                           nullptr,nullptr,"%08X",ImGuiInputTextFlags_CharsHexadecimal);
        if(ImGui::Button("Link Current Selector to Saved Scene"))
            changed(bridge.alias(alias_target));
    }
    ImGui::SeparatorText("Sky Illumination (additive fill)");
    int sky_strength=0,skycolor[3]={186,209,255},skyface=-1;
    for(int i=0;i<CVIII_SCENE_AMBIENT_MAX;++i){
        const CviiiSceneAmbient &a=s->scenes[i];
        if(!a.used || a.room!=room)continue;
        sky_strength=a.sky;
        if(a.sky){skycolor[0]=a.sky_red;skycolor[1]=a.sky_green;skycolor[2]=a.sky_blue;}
        skyface=a.sky_facing;
        break;
    }
    if(ImGui::SliderInt("Sky Strength",&sky_strength,0,100,"%d%%"))
        changed(bridge.sky(0,sky_strength));
    float color[3]={skycolor[0]/255.f,skycolor[1]/255.f,skycolor[2]/255.f};
    if(ImGui::ColorEdit3("Sky Light",color,ImGuiColorEditFlags_PickerHueWheel))
        for(int i=0;i<3;++i)
            changed(bridge.sky(i+1,(int)(color[i]*255.f+0.5f)));
    int sky_dir=skyface+1;
    if(ImGui::Combo("Sky Direction",&sky_dir,
                    "Upper Sky\0Uniform Fill\0Lower Bounce\0"))
        changed(bridge.sky(4,sky_dir-1));
    if(ImGui::Button("Neutralize Ambient Tint")){
        for(int i=1;i<=3;++i)changed(bridge.scene(i,255));
    }
    ImGui::TextDisabled("2D sky fill; not geometry-aware GI.");
    ImGui::TextDisabled("Real ReShade overlay. CVIII owns gameplay light pixels.");
    if(placement_pending && ImGui::IsMouseClicked(ImGuiMouseButton_Left) &&
       !ImGui::IsWindowHovered(ImGuiHoveredFlags_AnyWindow)){
        const ImVec2 pos=ImGui::GetIO().MousePos;
        if(pos.x>=0 && pos.y>=0 &&
           (pending_kit_kind>=0?
             bridge.place_kit_window(pending_kit_kind,pending_kit_id,
                                     (int)pos.x,(int)pos.y):
             bridge.place_window((int)pos.x,(int)pos.y))){
            bridge.save();
            placement_pending=false;pending_kit_kind=-1;
        }
    }
}
} // namespace

BOOL WINAPI DllMain(HINSTANCE module,DWORD reason,LPVOID){
    if(reason==DLL_PROCESS_ATTACH){
        if(!reshade::register_addon(module))return FALSE;
        reshade::register_event<reshade::addon_event::reshade_present>(&on_present);
        reshade::register_overlay("CVIII Lighting",&on_overlay);
    }else if(reason==DLL_PROCESS_DETACH){
        end_session();
        reshade::unregister_addon(module);
    }
    return TRUE;
}
