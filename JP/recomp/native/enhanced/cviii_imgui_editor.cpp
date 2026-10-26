/* CVIII Enhanced — real Dear ImGui lighting editor (SDL2 + SDL_Renderer).
 * All original NES game/PPU state is read-only. Dear ImGui is fetched
 * externally at a pinned release under its MIT license, not vendored.
 */
#include "cviii_imgui_editor.h"
#include "cviii_lighting_host.h"
#include "imgui.h"
#include "imgui_impl_sdl2.h"
#include "imgui_impl_sdlrenderer2.h"
#include <algorithm>
#include <cstdio>
#include <cctype>
#include <cstring>

namespace {
bool ready=false, place_pending=false, dirty=false;
int pending_kit_type=-1,pending_kit_id=-1; /* 0 builtin, 1 saved custom */
char kit_capture_name[CVIII_LIGHT_NAME_CAP]="My Lighting Rig";
int kit_capture_slot=0;
int global_style_slot=0,selected_mask=0;
bool draw_mask=false,mask_first=false;
int mask_x0=0,mask_y0=0;
char global_style_name[CVIII_LIGHT_NAME_CAP]="Torch Global";
unsigned alias_target=0,last_raw_room=0;
char search_text[64]={};
int current_tab=0;
SDL_Window *active_window=nullptr;
SDL_Renderer *active_renderer=nullptr;
ImVec2 panel_min(0,0), panel_max(0,0);
constexpr ImU32 cyan=IM_COL32(49,201,228,255);
constexpr ImU32 amber=IM_COL32(255,207,91,255);

bool init(SDL_Window *win,SDL_Renderer *renderer) {
    if(ready) return win==active_window && renderer==active_renderer;
    if(!win || !renderer)return false;
    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGuiIO &io=ImGui::GetIO();
    io.IniFilename=nullptr; // No incidental working-directory writes.
    io.ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;
    ImGui::StyleColorsDark();
    ImGuiStyle &style=ImGui::GetStyle();
    style.WindowRounding=8.0f;
    style.FrameRounding=4.0f;
    style.GrabRounding=4.0f;
    style.WindowPadding=ImVec2(14,12);
    style.ItemSpacing=ImVec2(8,9);
    style.Colors[ImGuiCol_WindowBg]=ImVec4(.055f,.073f,.098f,.97f);
    style.Colors[ImGuiCol_Header]=ImVec4(.12f,.36f,.43f,1.f);
    style.Colors[ImGuiCol_HeaderHovered]=ImVec4(.16f,.45f,.55f,1.f);
    style.Colors[ImGuiCol_HeaderActive]=ImVec4(.13f,.52f,.62f,1.f);
    style.Colors[ImGuiCol_SliderGrab]=ImVec4(.16f,.70f,.82f,1.f);
    style.Colors[ImGuiCol_SliderGrabActive]=ImVec4(.3f,.87f,.95f,1.f);
    style.Colors[ImGuiCol_CheckMark]=ImVec4(.20f,.80f,.90f,1.f);
    style.Colors[ImGuiCol_Button]=ImVec4(.15f,.30f,.38f,1.f);
    style.Colors[ImGuiCol_ButtonHovered]=ImVec4(.22f,.48f,.56f,1.f);
    if(!ImGui_ImplSDL2_InitForSDLRenderer(win,renderer)){
        ImGui::DestroyContext();return false;
    }
    if(!ImGui_ImplSDLRenderer2_Init(renderer)){
        ImGui_ImplSDL2_Shutdown();ImGui::DestroyContext();return false;
    }
    active_window=win;active_renderer=renderer;ready=true;
    return true;
}
bool contains_ci(const char *text,const char *needle){
    if(!needle || !*needle)return true;
    if(!text)return false;
    for(;*text;++text){
        const char *a=text,*b=needle;
        while(*a && *b &&
              std::tolower((unsigned char)*a)==std::tolower((unsigned char)*b)){
            ++a;++b;
        }
        if(!*b)return true;
    }
    return false;
}
bool within_panel(int x,int y) {
    return x>=panel_min.x && x<panel_max.x &&
           y>=panel_min.y && y<panel_max.y;
}
void maybe_change(int property,int value){
    if(cviii_lighting_editor_property(property,value))dirty=true;
}
void ui_handles(SDL_Renderer *renderer) {
    // Get 256x240 -> window coordinate conversion BEFORE disabling the
    // SDL game's logical scaling for sharp, desktop-sized ImGui controls.
    (void)renderer;
}
} // namespace

/* SDL_RenderSetLogicalSize() makes SDL2 rewrite mouse events into
 * NES 256x240 logical coordinates. Dear ImGui's SDL2 backend, however,
 * computes io.DisplaySize using SDL_GetWindowSize(). Restore window
 * coordinates BEFORE forwarding the event, including drag/motion.
 * SDL_RenderLogicalToWindow also accounts for letterboxing and resizing. */
extern "C" void cviii_imgui_window_point(SDL_Renderer *r,int ex,int ey,
                                          int *wx,int *wy){
    if(!wx || !wy)return;
    *wx=ex;*wy=ey;
    if(!r)return;
    int lw=0,lh=0;
    SDL_RenderGetLogicalSize(r,&lw,&lh);
    if(lw>0 && lh>0)
        SDL_RenderLogicalToWindow(r,(float)ex,(float)ey,wx,wy);
}
extern "C" int cviii_imgui_event(const SDL_Event *e,SDL_Window *w,SDL_Renderer *r){
    if(!e || cviii_lighting_editor_external_active() || !cviii_lighting_editor_active() || !init(w,r))return 0;
    SDL_Event window_event=*e;
    if(e->type==SDL_MOUSEMOTION){
        cviii_imgui_window_point(r,e->motion.x,e->motion.y,
                                 &window_event.motion.x,&window_event.motion.y);
    }else if(e->type==SDL_MOUSEBUTTONDOWN || e->type==SDL_MOUSEBUTTONUP){
        cviii_imgui_window_point(r,e->button.x,e->button.y,
                                 &window_event.button.x,&window_event.button.y);
    }
    ImGui_ImplSDL2_ProcessEvent(&window_event);
    switch(e->type){
    case SDL_MOUSEBUTTONDOWN:
    case SDL_MOUSEBUTTONUP: {
        const int x=window_event.button.x,y=window_event.button.y;
        return within_panel(x,y)||ImGui::GetIO().WantCaptureMouse;
    }
    case SDL_MOUSEMOTION:
        return within_panel(window_event.motion.x,window_event.motion.y)||
               ImGui::GetIO().WantCaptureMouse;
    case SDL_MOUSEWHEEL: {
        int x=0,y=0;SDL_GetMouseState(&x,&y);
        return within_panel(x,y)||ImGui::GetIO().WantCaptureMouse;
    }
    case SDL_TEXTINPUT:
        return ImGui::GetIO().WantTextInput;
    case SDL_KEYDOWN:
        if(ImGui::GetIO().WantCaptureKeyboard)return 1;
        if((e->key.keysym.mod & KMOD_CTRL) &&
           (e->key.keysym.scancode==SDL_SCANCODE_C ||
            e->key.keysym.scancode==SDL_SCANCODE_V ||
            e->key.keysym.scancode==SDL_SCANCODE_D))return 1;
        return 0;
    default: return 0;
    }
}
extern "C" int cviii_imgui_scene_click(int event,int x,int y){
    if(!cviii_lighting_editor_active() || event!=2)return 0;
    if(draw_mask){
        int wx=0,wy=0;
        if(!cviii_lighting_editor_world_point(x,y,&wx,&wy))return 1;
        if(!mask_first){
            mask_x0=wx;mask_y0=wy;mask_first=true;
            return 1;
        }
        int left=wx<mask_x0?wx:mask_x0;
        int top=wy<mask_y0?wy:mask_y0;
        int width=(wx>mask_x0?wx-mask_x0:mask_x0-wx)+1;
        int height=(wy>mask_y0?wy-mask_y0:mask_y0-wy)+1;
        int m=cviii_lighting_editor_mask_add(left,top,width,height);
        if(m>=0){
            selected_mask=m;draw_mask=false;mask_first=false;dirty=true;
            return 2;
        }
        return 1;
    }
    if(!place_pending && pending_kit_type<0)return 0;
    int ok=pending_kit_type==0?
        cviii_lighting_editor_apply_builtin(pending_kit_id,x,y):
        pending_kit_type==1?
        cviii_lighting_editor_apply_kit(pending_kit_id,x,y):
        cviii_lighting_editor_add(x,y);
    if(ok){
        place_pending=false;pending_kit_type=-1;pending_kit_id=-1;dirty=true;
    }
    return ok?2:1;
}
extern "C" void cviii_imgui_reset(void){
    place_pending=false;
    pending_kit_type=-1;pending_kit_id=-1;
    draw_mask=false;mask_first=false;
    panel_min=ImVec2(0,0);panel_max=ImVec2(0,0);
}
extern "C" void cviii_imgui_shutdown(void){
    if(ready){
        ImGui_ImplSDLRenderer2_Shutdown();
        ImGui_ImplSDL2_Shutdown();
        ImGui::DestroyContext();
    }
    ready=false;dirty=false;place_pending=false;
    active_window=nullptr;active_renderer=nullptr;
}
extern "C" int cviii_imgui_render(SDL_Window *window,SDL_Renderer *renderer){
    if(cviii_lighting_editor_external_active())return 0;
    if(!cviii_lighting_editor_active()){
        cviii_imgui_reset();return 0;
    }
    if(!init(window,renderer))return 0;
    // The game's sprite layer is already rendered in 256x240 logical
    // coordinates. Use physical/window-sized pixels for UI readability.
    int native_w=0,native_h=0;
    SDL_RenderGetLogicalSize(renderer,&native_w,&native_h);
    int viewport_x=0,viewport_y=0;
    (void)viewport_x;(void)viewport_y;
    SDL_RenderSetLogicalSize(renderer,0,0);
    SDL_RenderSetScale(renderer,1.0f,1.0f);
    ImGui_ImplSDLRenderer2_NewFrame();
    ImGui_ImplSDL2_NewFrame();
    ImGui::NewFrame();

    int ww=0,wh=0;SDL_GetWindowSize(window,&ww,&wh);
    const float window_width=ww>500?420.0f:std::max(310.f,(float)ww-28.f);
    ImGui::SetNextWindowSize(ImVec2(window_width,std::min(680.f,(float)wh-28.f)),
                             ImGuiCond_FirstUseEver);
    ImGui::SetNextWindowPos(ImVec2(std::max(8.f,(float)ww-window_width-18.f),14.f),
                            ImGuiCond_FirstUseEver);
    bool stay_open=true;
    ImGui::Begin("CVIII  |  LIGHTING STUDIO",&stay_open,
                 ImGuiWindowFlags_NoCollapse|ImGuiWindowFlags_NoSavedSettings);
    panel_min=ImGui::GetWindowPos();
    panel_max=ImVec2(panel_min.x+ImGui::GetWindowWidth(),
                     panel_min.y+ImGui::GetWindowHeight());
    const CviiiLighting *model=cviii_lighting_editor_model();
    const unsigned room=cviii_lighting_editor_room();
    bool enabled=model->enabled!=0;
    ImGui::TextColored(ImVec4(.65f,.81f,.92f,1.f),"LIGHTING STUDIO");
    ImGui::SameLine();
    ImGui::TextDisabled("  HOME: TOGGLE  /  CTRL+HOME: REBIND");
    ImGui::Separator();
    if(ImGui::Button("Undo (Ctrl+Z)",ImVec2(133,25))){
        if(cviii_lighting_editor_undo())dirty=true;
    }
    ImGui::SameLine();
    if(ImGui::Button("Redo (Ctrl+Y)",ImVec2(133,25))){
        if(cviii_lighting_editor_redo())dirty=true;
    }
    if(ImGui::GetIO().KeyCtrl && !ImGui::GetIO().WantTextInput){
        if(ImGui::IsKeyPressed(ImGuiKey_Z,false) &&
           cviii_lighting_editor_undo())dirty=true;
        if(ImGui::IsKeyPressed(ImGuiKey_Y,false) &&
           cviii_lighting_editor_redo())dirty=true;
    }
    /* Familiar ReShade workflow: Home to pick effects; scene and settings
       tabs for common controls; search and categorized effect list. This
       native Dear ImGui pane is not ReShade's injected overlay itself. */
    if(ImGui::BeginTabBar("##LightingTabs",ImGuiTabBarFlags_None)){
        if(ImGui::BeginTabItem("Home")){
            current_tab=0;
            ImGui::Checkbox("Enable effects",&enabled);
            if(enabled!=(model->enabled!=0))maybe_change(0,enabled?1:0);
            ImGui::SameLine();
            ImGui::TextDisabled("Scene %08X",room);
            ImGui::SetNextItemWidth(-1.f);
            ImGui::InputTextWithHint("##Search","Search names, groups, light types...",
                                     search_text,sizeof search_text);
            if(ImGui::Button(place_pending?"PLACE: CLICK SCENE":"Add Light",ImVec2(115,27))){
                place_pending=true;pending_kit_type=-1;pending_kit_id=-1;
            }
            ImGui::SameLine();
            if(ImGui::Button("Duplicate",ImVec2(82,27)))
                if(cviii_lighting_editor_duplicate())dirty=true;
            ImGui::SameLine();
            if(ImGui::Button("Delete",ImVec2(68,27)))
                if(cviii_lighting_editor_input(5,-1,-1))dirty=true;
            if(ImGui::Button("Copy",ImVec2(65,25)))
                (void)cviii_lighting_editor_copy();
            ImGui::SameLine();
            if(ImGui::Button("Paste",ImVec2(65,25)))
                if(cviii_lighting_editor_paste())dirty=true;
            ImGui::SameLine();
            ImGui::TextDisabled("Ctrl+C / Ctrl+V / Ctrl+D");
            if(ImGui::GetIO().KeyCtrl && !ImGui::GetIO().WantTextInput){
                if(ImGui::IsKeyPressed(ImGuiKey_C,false))
                    (void)cviii_lighting_editor_copy();
                if(ImGui::IsKeyPressed(ImGuiKey_V,false) && cviii_lighting_editor_paste())
                    dirty=true;
                if(ImGui::IsKeyPressed(ImGuiKey_D,false) && cviii_lighting_editor_duplicate())
                    dirty=true;
            }
            ImGui::SeparatorText("Effect List   /   Lights by Group");
            if(ImGui::BeginChild("##LightingList",ImVec2(0,177),
                                  ImGuiChildFlags_Borders)){
                char group_names[CVIII_LIGHT_MAX][CVIII_LIGHT_GROUP_CAP]={};
                int group_count=0,matched=0;
                for(int i=0;i<CVIII_LIGHT_MAX;++i){
                    const CviiiLight &l=model->light[i];
                    if(!l.used || l.room!=room)continue;
                    const char *grp=l.group[0]?l.group:"Ungrouped";
                    int seen=0;
                    for(int g=0;g<group_count;++g)
                        if(!std::strcmp(group_names[g],grp)){seen=1;break;}
                    if(!seen && group_count<CVIII_LIGHT_MAX){
                        std::snprintf(group_names[group_count],
                                      sizeof group_names[0],"%s",grp);
                        ++group_count;
                    }
                }
                for(int g=0;g<group_count;++g){
                    ImGui::PushID(g);
                    const char *group=group_names[g];
                    bool open=ImGui::TreeNodeEx(group,
                        ImGuiTreeNodeFlags_DefaultOpen|ImGuiTreeNodeFlags_SpanAvailWidth);
                    if(open){
                        for(int i=0;i<CVIII_LIGHT_MAX;++i){
                            const CviiiLight &l=model->light[i];
                            if(!l.used || l.room!=room)continue;
                            const char *grp=l.group[0]?l.group:"Ungrouped";
                            if(std::strcmp(grp,group))continue;
                            char fallback[32];
                            std::snprintf(fallback,sizeof fallback,"Light %02d",i+1);
                            const char *name=l.name[0]?l.name:fallback;
                            if(!contains_ci(name,search_text) &&
                               !contains_ci(group,search_text))continue;
                            ++matched;
                            ImGui::PushID(i);
                            bool visible=!l.muted;
                            if(ImGui::Checkbox("##Enable",&visible)){
                                (void)cviii_lighting_editor_select(i);
                                maybe_change(11,visible?0:1);
                            }
                            ImGui::SameLine();
                            char title[120];
                            const char *kind=l.shape==CVIII_SHAPE_CONE?"Cone":
                                l.shape==CVIII_SHAPE_SHAFT?"Shaft":"Radial";
                            std::snprintf(title,sizeof title,
                                          "%s   [%s]   %d,%d",name,kind,l.x,l.y);
                            if(ImGui::Selectable(title,model->selected==i))
                                (void)cviii_lighting_editor_select(i);
                            ImGui::PopID();
                        }
                        ImGui::TreePop();
                    }
                    ImGui::PopID();
                }
                if(!matched)
                    ImGui::TextDisabled("No matching lights. Use Add Light to create one.");
            }
            ImGui::EndChild();
            const int selected=model->selected;
            if(selected>=0 && selected<CVIII_LIGHT_MAX &&
               model->light[selected].used && model->light[selected].room==room){
                const CviiiLight &light=model->light[selected];
                ImGui::SeparatorText("Light Properties");
                char label[CVIII_LIGHT_NAME_CAP];
                std::snprintf(label,sizeof label,"%s",light.name);
                if(ImGui::InputText("Name",label,sizeof label))
                    if(cviii_lighting_editor_name(label))dirty=true;
                char group[CVIII_LIGHT_GROUP_CAP];
                std::snprintf(group,sizeof group,"%s",light.group);
                if(ImGui::InputText("Group",group,sizeof group))
                    if(cviii_lighting_editor_group(group))dirty=true;
                int shape=light.shape;
                if(ImGui::Combo("Shape",&shape,"Radial (point)\0Spot cone\0Light shaft\0"))
                    maybe_change(7,shape);
                int posx=light.x,posy=light.y;
                if(ImGui::InputInt("World X",&posx,1,16))maybe_change(13,posx);
                if(ImGui::InputInt("World Y",&posy,1,8))maybe_change(14,posy);
                int radius=light.radius,energy=light.energy;
                if(ImGui::SliderInt("Range",&radius,12,160,"%d px"))
                    maybe_change(2,radius);
                if(ImGui::SliderInt("Intensity",&energy,5,160,"%d"))
                    maybe_change(3,energy);
                if(shape!=CVIII_SHAPE_RADIAL){
                    int angle=light.angle;
                    if(ImGui::SliderInt("Direction",&angle,0,359,"%d deg"))
                        maybe_change(8,angle);
                    if(shape==CVIII_SHAPE_CONE){
                        int spread=light.spread?light.spread:30;
                        if(ImGui::SliderInt("Beam angle",&spread,5,85,"%d deg"))
                            maybe_change(9,spread);
                    }else{
                        int width=light.width?light.width:32;
                        if(ImGui::SliderInt("Shaft width",&width,4,160,"%d px"))
                            maybe_change(10,width);
                    }
                }
                float rgb[3]={light.red/255.f,light.green/255.f,light.blue/255.f};
                if(ImGui::ColorEdit3("Color",rgb,
                    ImGuiColorEditFlags_PickerHueWheel|ImGuiColorEditFlags_DisplayRGB)){
                    maybe_change(4,(int)(rgb[0]*255.f+0.5f));
                    maybe_change(5,(int)(rgb[1]*255.f+0.5f));
                    maybe_change(6,(int)(rgb[2]*255.f+0.5f));
                }
                int flicker=light.flicker;
                if(ImGui::Combo("Flame animation",&flicker,
                    "Candle flicker\0Steady\0Torch turbulence\0Soft pulse\0Ember dips\0"))
                    maybe_change(12,flicker);
                if(flicker!=1){
                    int speed=light.anim_speed,depth=light.anim_strength;
                    if(ImGui::SliderInt("Flame Speed",&speed,0,400,
                                       speed?"%d%%":"Auto"))
                        maybe_change(15,speed);
                    if(ImGui::SliderInt("Flame Strength",&depth,0,100,
                                       depth?"%d%%":"Auto"))
                        maybe_change(16,depth);
                    ImGui::TextDisabled("Auto preserves earlier profiles; animation is frame driven.");
                }
                if(ImGui::Button("Warm candle")){
                    maybe_change(4,255);maybe_change(5,167);maybe_change(6,74);
                }
                ImGui::SameLine();
                if(ImGui::Button("Cold blue")){
                    maybe_change(4,150);maybe_change(5,196);maybe_change(6,255);
                }
                ImGui::SameLine();
                if(ImGui::Button("White")){
                    maybe_change(4,255);maybe_change(5,255);maybe_change(6,255);
                }
            }else ImGui::TextDisabled("Select a light from the list to edit it.");
            ImGui::EndTabItem();
        }
        if(ImGui::BeginTabItem("Library")){
            current_tab=5;
            ImGui::TextWrapped("Global rigs are reusable named sets of emitters. "
                "Apply at camera center, or click Place and select a spot "
                "in the level. All lights become part of the current room.");
            ImGui::SeparatorText("Built-in Global Rigs");
            for(int i=0;i<cviii_light_builtin_count();++i){
                ImGui::PushID(i);
                ImGui::TextUnformatted(cviii_light_builtin_name(i));
                ImGui::SameLine(185);
                if(ImGui::SmallButton("Apply Here")){
                    if(cviii_lighting_editor_apply_builtin(i,-1,-1))dirty=true;
                }
                ImGui::SameLine();
                if(ImGui::SmallButton("Place...")){
                    pending_kit_type=0;pending_kit_id=i;place_pending=false;
                }
                ImGui::PopID();
            }
            ImGui::SeparatorText("Your Global Kits");
            ImGui::SetNextItemWidth(-100.f);
            ImGui::InputText("Kit name",kit_capture_name,sizeof kit_capture_name);
            ImGui::SliderInt("Library slot",&kit_capture_slot,0,CVIII_KIT_MAX-1);
            if(ImGui::Button("Save Selected Group as Global Kit")){
                if(cviii_lighting_editor_capture_kit(kit_capture_slot,kit_capture_name))
                    dirty=true;
            }
            if(model->kits[kit_capture_slot].used){
                if(ImGui::Button("Rename Saved Kit")){
                    if(cviii_lighting_editor_kit_manage(
                         1,kit_capture_slot,-1,kit_capture_name))dirty=true;
                }
                ImGui::SameLine();
                if(ImGui::Button("Duplicate to Empty Slot")){
                    int empty=-1;
                    for(int i=0;i<CVIII_KIT_MAX;++i)
                        if(!model->kits[i].used){empty=i;break;}
                    if(empty>=0 && cviii_lighting_editor_kit_manage(
                          2,kit_capture_slot,empty,nullptr)){
                        kit_capture_slot=empty;dirty=true;
                    }
                }
                ImGui::SameLine();
                if(ImGui::Button("Delete Saved Kit")){
                    if(cviii_lighting_editor_kit_manage(
                         3,kit_capture_slot,-1,nullptr))dirty=true;
                }
            }
            ImGui::TextDisabled("Captures the selected light and up to %d "
                                "members of the same named group.",
                                CVIII_KIT_PARTS);
            for(int k=0;k<CVIII_KIT_MAX;++k){
                if(!model->kits[k].used)continue;
                ImGui::PushID(k+1000);
                ImGui::Text("%02d. %s (%d emitters)",k+1,model->kits[k].name,
                            model->kits[k].count);
                ImGui::SameLine(210);
                if(ImGui::SmallButton("Apply")){
                    if(cviii_lighting_editor_apply_kit(k,-1,-1))dirty=true;
                }
                ImGui::SameLine();
                if(ImGui::SmallButton("Place")){
                    pending_kit_type=1;pending_kit_id=k;place_pending=false;
                }
                ImGui::PopID();
            }
            if(pending_kit_type>=0){
                ImGui::TextColored(ImVec4(.9f,.75f,.3f,1.f),
                    "PLACEMENT ACTIVE - click the exposed gameplay");
                if(ImGui::Button("Cancel Placement")){
                    pending_kit_type=-1;pending_kit_id=-1;place_pending=false;
                }
            }
            ImGui::EndTabItem();
        }
        if(ImGui::BeginTabItem("Global Styles")){
            current_tab=6;
            ImGui::TextWrapped("Capture one authored light as a GLOBAL STYLE. "
                "Link a single light or its whole named group to it. "
                "Changing the style then updates every linked instance "
                "in every room while preserving individual positions.");
            ImGui::InputText("Global Style Name",global_style_name,
                              sizeof global_style_name);
            ImGui::SliderInt("Style Slot",&global_style_slot,0,
                              CVIII_GLOBAL_STYLE_MAX-1);
            if(ImGui::Button("Capture Selected As Global Style")){
                if(cviii_lighting_editor_global_capture(global_style_slot,
                      global_style_name))dirty=true;
            }
            if(ImGui::Button("Link Selected")){
                if(cviii_lighting_editor_global_link(global_style_slot,0))
                    dirty=true;
            }
            ImGui::SameLine();
            if(ImGui::Button("Link Current Group")){
                if(cviii_lighting_editor_global_link(global_style_slot,1))
                    dirty=true;
            }
            ImGui::SameLine();
            if(ImGui::Button("Unlink Selected")){
                if(cviii_lighting_editor_global_link(-1,0))dirty=true;
            }
            ImGui::SeparatorText("Shared Appearance");
            const CviiiGlobalStyle &gs=model->styles[global_style_slot];
            if(gs.used){
                ImGui::Text("Editing: %s",gs.name);
                int radius=gs.light.radius,energy=gs.light.energy;
                if(ImGui::SliderInt("Global Range",&radius,12,160))
                    if(cviii_lighting_editor_global_property(
                       global_style_slot,2,radius))dirty=true;
                if(ImGui::SliderInt("Global Strength",&energy,5,160))
                    if(cviii_lighting_editor_global_property(
                       global_style_slot,3,energy))dirty=true;
                float rgb[3]={gs.light.red/255.f,gs.light.green/255.f,
                              gs.light.blue/255.f};
                if(ImGui::ColorEdit3("Global Color",rgb,
                     ImGuiColorEditFlags_PickerHueWheel|ImGuiColorEditFlags_DisplayRGB)){
                    for(int i=0;i<3;++i)
                        if(cviii_lighting_editor_global_property(
                          global_style_slot,4+i,(int)(rgb[i]*255.f+0.5f)))
                            dirty=true;
                }
                int shape=gs.light.shape;
                if(ImGui::Combo("Global Shape",&shape,
                                "Radial\0Cone\0Shaft\0"))
                    if(cviii_lighting_editor_global_property(
                       global_style_slot,7,shape))dirty=true;
                int angle=gs.light.angle;
                if(ImGui::SliderInt("Global Angle",&angle,0,359))
                    if(cviii_lighting_editor_global_property(
                       global_style_slot,8,angle))dirty=true;
                int width=gs.light.width?gs.light.width:32;
                if(ImGui::SliderInt("Global Shaft Width",&width,4,160))
                    if(cviii_lighting_editor_global_property(
                       global_style_slot,10,width))dirty=true;
                int motion=gs.light.flicker;
                if(ImGui::Combo("Shared Animation",&motion,
                    "Candle\0Steady\0Torch\0Pulse\0Ember\0"))
                    if(cviii_lighting_editor_global_property(
                       global_style_slot,12,motion))dirty=true;
                if(motion!=1){
                    int speed=gs.light.anim_speed,depth=gs.light.anim_strength;
                    if(ImGui::SliderInt("Shared Flame Speed",&speed,0,400))
                        if(cviii_lighting_editor_global_property(
                           global_style_slot,15,speed))dirty=true;
                    if(ImGui::SliderInt("Shared Flame Strength",&depth,0,100))
                        if(cviii_lighting_editor_global_property(
                           global_style_slot,16,depth))dirty=true;
                }
            }else ImGui::TextDisabled("Choose a slot and capture a light first.");
            ImGui::SeparatorText("Saved Global Styles");
            for(int i=0;i<CVIII_GLOBAL_STYLE_MAX;++i){
                if(!model->styles[i].used)continue;
                ImGui::PushID(i);
                if(ImGui::Selectable(model->styles[i].name,i==global_style_slot))
                    global_style_slot=i;
                ImGui::PopID();
            }
            ImGui::EndTabItem();
        }
        if(ImGui::BeginTabItem("Scene")){
            current_tab=1;
            ImGui::Text("Scene: %08X",room);
            ImGui::TextDisabled("These settings are specific to this stage/room.");
            ImGui::SeparatorText("Environment / Ambient Illumination");
            int level=0,color[3]={255,255,255};
            cviii_light_scene_get(model,room,&level,color);
            if(ImGui::SliderInt("Ambient Strength",&level,0,100,"%d%%"))
                if(cviii_lighting_editor_scene(0,level))dirty=true;
            float tint[3]={color[0]/255.f,color[1]/255.f,color[2]/255.f};
            if(ImGui::ColorEdit3("Ambient Tint",tint,
                    ImGuiColorEditFlags_PickerHueWheel|ImGuiColorEditFlags_DisplayRGB)){
                for(int i=0;i<3;++i)
                    if(cviii_lighting_editor_scene(i+1,
                         (int)(tint[i]*255.f+0.5f)))dirty=true;
            }
            if(ImGui::Button("Neutral white ambient (recommended)")){
                for(int i=0;i<3;++i)
                    if(cviii_lighting_editor_scene(i+1,255))dirty=true;
            }
            ImGui::SeparatorText("Independent Sky / Hemisphere Fill");
            int sky_strength=0,sky_rgb[3],sky_direction=-1;
            cviii_light_sky_get(model,room,&sky_strength,sky_rgb,&sky_direction);
            if(ImGui::SliderInt("Sky Brightness",&sky_strength,0,100,"%d%%"))
                if(cviii_lighting_editor_sky(0,sky_strength))dirty=true;
            float sky_color[3]={sky_rgb[0]/255.f,sky_rgb[1]/255.f,sky_rgb[2]/255.f};
            if(ImGui::ColorEdit3("Sky Light Color",sky_color,
                    ImGuiColorEditFlags_PickerHueWheel|ImGuiColorEditFlags_DisplayRGB)){
                for(int i=0;i<3;++i)
                    if(cviii_lighting_editor_sky(i+1,
                       (int)(sky_color[i]*255.f+0.5f)))dirty=true;
            }
            int direction=sky_direction+1;
            if(ImGui::Combo("Sky Gradient Direction",&direction,
                            "Upper sky\0Uniform fill\0Lower bounce\0"))
                if(cviii_lighting_editor_sky(4,direction-1))dirty=true;
            if(ImGui::Button("Daylight")){
                if(cviii_lighting_editor_sky(0,32))dirty=true;
                const int c[3]={204,224,255};
                for(int i=0;i<3;++i)
                    if(cviii_lighting_editor_sky(i+1,c[i]))dirty=true;
                if(cviii_lighting_editor_sky(4,-1))dirty=true;
            }
            ImGui::SameLine();
            if(ImGui::Button("Moonlight")){
                if(cviii_lighting_editor_sky(0,20))dirty=true;
                const int c[3]={123,157,245};
                for(int i=0;i<3;++i)
                    if(cviii_lighting_editor_sky(i+1,c[i]))dirty=true;
                if(cviii_lighting_editor_sky(4,-1))dirty=true;
            }
            ImGui::SameLine();
            if(ImGui::Button("No Sky")){
                if(cviii_lighting_editor_sky(0,0))dirty=true;
            }
            ImGui::TextWrapped("Sky fill adds softly lit color without "
                "subtracting palette channels. It is art-directed 2D "
                "hemispherical fill, not true bounce-light GI.");
            ImGui::SeparatorText("Scene Grading");
            int ev=0,temp=0,sat=100;
            cviii_light_grade_get(model,room,&ev,&temp,&sat);
            if(ImGui::SliderInt("Exposure (EV x100)",&ev,-200,200,"%+d"))
                if(cviii_lighting_editor_grade(0,ev))dirty=true;
            if(ImGui::SliderInt("White Balance / Temperature",&temp,-100,100))
                if(cviii_lighting_editor_grade(1,temp))dirty=true;
            if(ImGui::SliderInt("Saturation",&sat,0,200,"%d%%"))
                if(cviii_lighting_editor_grade(2,sat))dirty=true;
            if(ImGui::Button("Neutral Grade (reset)")){
                if(cviii_lighting_editor_grade(0,0))dirty=true;
                if(cviii_lighting_editor_grade(1,0))dirty=true;
                if(cviii_lighting_editor_grade(2,100))dirty=true;
            }
            ImGui::SeparatorText("Authoring Notes");
            ImGui::BulletText("Lighting only changes final presentation pixels.");
            ImGui::BulletText("Emitters are attached to candidate room IDs.");
            ImGui::BulletText("Geometry-based cast shadows are not yet available.");
            ImGui::BulletText("Lights beyond the screen are culled by their footprint.");
            ImGui::EndTabItem();
        }
        if(ImGui::BeginTabItem("Masks")){
            current_tab=7;
            ImGui::TextWrapped("Manually author occluder rectangles over walls. "
                "Only these masks cast soft shadows from local emitters. "
                "Sky and ambient remain unobstructed; no tile collision "
                "geometry is inferred.");
            const int chosen=model->selected;
            if(chosen>=0 && chosen<CVIII_LIGHT_MAX &&
               model->light[chosen].used && model->light[chosen].room==room){
                if(ImGui::Button("Add Mask Near Selected Light")){
                    int x=model->light[chosen].x+18;
                    int y=model->light[chosen].y-15;
                    if(y<CVIII_LIGHT_HUD)y=CVIII_LIGHT_HUD;
                    int index=cviii_lighting_editor_mask_add(x,y,10,30);
                    if(index>=0){selected_mask=index;dirty=true;}
                }
            }else ImGui::TextDisabled("Select a scene light before adding a mask.");
            if(ImGui::Button(draw_mask?"DRAW MASK: CLICK 2 CORNERS":"Draw Rectangle on Level")){
                draw_mask=true;mask_first=false;
                place_pending=false;pending_kit_type=-1;pending_kit_id=-1;
            }
            if(draw_mask){
                ImGui::TextColored(ImVec4(.9f,.78f,.32f,1.f),
                    mask_first?"Click opposite rectangle corner":"Click first rectangle corner");
                ImGui::SameLine();
                if(ImGui::SmallButton("Cancel Draw")){
                    draw_mask=false;mask_first=false;
                }
            }
            ImGui::SeparatorText("Room Occluders");
            for(int i=0;i<CVIII_OCCLUDER_MAX;++i){
                if(!model->masks[i].used || model->masks[i].room!=room)continue;
                ImGui::PushID(i);
                char name[48];
                std::snprintf(name,sizeof name,"Mask %02d",i+1);
                if(ImGui::Selectable(name,i==selected_mask))selected_mask=i;
                ImGui::PopID();
            }
            if(selected_mask>=0 && selected_mask<CVIII_OCCLUDER_MAX &&
               model->masks[selected_mask].used &&
               model->masks[selected_mask].room==room){
                const CviiiOccluder &mask=model->masks[selected_mask];
                ImGui::SeparatorText("Selected Mask");
                int x=mask.x,y=mask.y,w=mask.w,h=mask.h,
                    opacity=mask.opacity,soft=mask.softness;
                if(ImGui::InputInt("World X##mask",&x))
                    if(cviii_lighting_editor_mask_property(selected_mask,1,x))dirty=true;
                if(ImGui::InputInt("World Y##mask",&y))
                    if(cviii_lighting_editor_mask_property(selected_mask,2,y))dirty=true;
                if(ImGui::SliderInt("Width##mask",&w,1,160))
                    if(cviii_lighting_editor_mask_property(selected_mask,3,w))dirty=true;
                if(ImGui::SliderInt("Height##mask",&h,1,160))
                    if(cviii_lighting_editor_mask_property(selected_mask,4,h))dirty=true;
                if(ImGui::SliderInt("Shadow Opacity",&opacity,0,100,"%d%%"))
                    if(cviii_lighting_editor_mask_property(selected_mask,5,opacity))dirty=true;
                if(ImGui::SliderInt("Soft Penumbra",&soft,0,CVIII_OCCLUDER_MAX_SOFTNESS,"%d px"))
                    if(cviii_lighting_editor_mask_property(selected_mask,6,soft))dirty=true;
                if(ImGui::Button("Delete Mask")){
                    if(cviii_lighting_editor_mask_property(selected_mask,0,0))
                        dirty=true;
                }
            }
            ImGui::TextDisabled("Mask outlines are visible only while editing.");
            ImGui::EndTabItem();
        }
        if(ImGui::BeginTabItem("Settings")){
            current_tab=2;
            ImGui::SeparatorText("Renderer Backend");
            int renderer=cviii_lighting_editor_renderer();
            if(ImGui::Combo("Lighting Mode",&renderer,
                    "Standard (CPU, always available)\0GPU Prototype (D3D11, one bounce)\0")){
                if(cviii_lighting_editor_set_renderer(renderer))dirty=true;
            }
            ImGui::TextWrapped("Standard uses the existing renderer. GPU Prototype "
                "traces the manually authored wall masks and samples a single "
                "diffuse bounce at 128x96. The original NES picture remains "
                "full resolution. This experimental pass uses a D3D11 compute "
                "device and reads back the light map; it is not Radiance Cascades.");
            ImGui::Text("Backend: %s",cviii_lighting_editor_gpu_status());
            ImGui::TextDisabled("While editing, Standard is shown for mask handles; "
                "GPU renders after closing the editor. If unavailable or over "
                "capacity, each frame automatically uses Standard.");
            ImGui::SeparatorText("Global Lighting");
            if(ImGui::Checkbox("Enable all lighting",&enabled))
                maybe_change(0,enabled?1:0);
            int global=model->ambient;
            if(ImGui::SliderInt("Default Ambient",&global,35,100,"%d%%"))
                maybe_change(1,global);
            ImGui::TextWrapped("The default ambient is used in rooms that "
                               "do not have an explicit scene setting.");
            ImGui::SeparatorText("Persistent Scene Identity");
            unsigned raw=cviii_lighting_editor_raw_room();
            if(raw!=last_raw_room){
                last_raw_room=raw;
                alias_target=room;
            }
            ImGui::Text("Raw selector: %08X   Resolved scene: %08X",raw,room);
            ImGui::TextWrapped("Lights stay in config.ini across deaths, "
                "reloads and stage exits. If the original game changes "
                "its room selector when you RETURN to this scene, link "
                "the new selector to its saved scene ID below.");
            ImGui::InputScalar("Saved Scene ID",ImGuiDataType_U32,&alias_target,
                              nullptr,nullptr,"%08X",
                              ImGuiInputTextFlags_CharsHexadecimal);
            if(ImGui::Button("Map This Raw Selector to Saved Scene")){
                if(cviii_lighting_editor_alias(alias_target))dirty=true;
            }
            ImGui::TextDisabled("Manual mapping; avoids silently merging unrelated rooms.");
            ImGui::SeparatorText("Editor Preferences");
            ImGui::Text("Toggle: %s",cviii_lighting_editor_key());
            ImGui::TextDisabled("Press Ctrl+Home to rebind the editor key.");
            ImGui::TextDisabled("Changes are automatically saved to config.ini.");
            ImGui::EndTabItem();
        }
        if(ImGui::BeginTabItem("Statistics")){
            current_tab=3;
            int total=0,visible=0,rooms=0;
            for(int i=0;i<CVIII_LIGHT_MAX;++i){
                if(!model->light[i].used)continue;
                ++total;
                if(model->light[i].room==room)++visible;
            }
            for(int i=0;i<CVIII_SCENE_AMBIENT_MAX;++i)
                if(model->scenes[i].used)++rooms;
            ImGui::Text("Lights authored: %d / %d",total,CVIII_LIGHT_MAX);
            ImGui::Text("Active scene emitters: %d",visible);
            ImGui::Text("Scene ambient overrides: %d / %d",
                        rooms,CVIII_SCENE_AMBIENT_MAX);
            ImGui::Text("Copy buffer: %s",
                        model->clipboard_valid?"Ready":"Empty");
            ImGui::TextWrapped("The original NES/PPU simulation is unchanged.");
            ImGui::EndTabItem();
        }
        if(ImGui::BeginTabItem("About")){
            current_tab=4;
            ImGui::TextUnformatted("CVIII Enhanced Lighting Studio");
            ImGui::Separator();
            ImGui::TextWrapped("Inspired by ReShade's overlay workflow, "
                               "and implemented with Dear ImGui + SDL2. "
                               "This native window is not the separate "
                               "ReShade injected overlay.");
            ImGui::TextDisabled("Original Japanese game state remains authoritative.");
            ImGui::EndTabItem();
        }
        ImGui::EndTabBar();
    }
    ImGui::Separator();
    if(ImGui::Button("Save Settings",ImVec2(120,30)))dirty=true;
    ImGui::SameLine();
    if(ImGui::Button("Resume Game",ImVec2(-1,30)))stay_open=false;
    ImGui::End();

    // Large, directly grab-able world-space scene centers, projected to
    // desktop pixel coordinates; no invented stage/map geometry.
    ImDrawList *draw=ImGui::GetBackgroundDrawList();
    for(int i=0;i<CVIII_LIGHT_MAX;++i){
        if(!model->light[i].used || model->light[i].room!=room)continue;
        int sx=0,sy=0;
        if(!cviii_lighting_editor_point(i,&sx,&sy))continue;
        // SDL_RenderLogicalToWindow expects the original game logical scale.
        SDL_RenderSetLogicalSize(renderer,native_w,native_h);
        int wx=0,wy=0;
        SDL_RenderLogicalToWindow(renderer,sx,sy,&wx,&wy);
        SDL_RenderSetLogicalSize(renderer,0,0);
        const ImVec2 pos((float)wx,(float)wy);
        if(within_panel(wx,wy))continue;
        const bool sel=i==model->selected;
        draw->AddCircleFilled(pos,sel?12.f:9.f,IM_COL32(12,18,26,215));
        draw->AddCircle(pos,sel?12.f:9.f,sel?amber:cyan,24,2.5f);
        draw->AddCircleFilled(pos,4.f,sel?amber:cyan);
    }

    ImGui::Render();
    SDL_RenderSetScale(renderer,ImGui::GetIO().DisplayFramebufferScale.x,
                                ImGui::GetIO().DisplayFramebufferScale.y);
    ImGui_ImplSDLRenderer2_RenderDrawData(ImGui::GetDrawData(),renderer);
    SDL_RenderSetLogicalSize(renderer,native_w,native_h);
    if(!stay_open){
        (void)cviii_lighting_editor_input(1,-1,-1);
        place_pending=false;pending_kit_type=-1;dirty=true;
    }
    if(dirty && !ImGui::IsMouseDown(ImGuiMouseButton_Left)){
        dirty=false;
        return 1; // caller owns existing atomic settings serialization
    }
    return 0;
}
