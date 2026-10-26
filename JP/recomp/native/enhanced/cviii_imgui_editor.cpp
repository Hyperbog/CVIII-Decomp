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
    if(!cviii_lighting_editor_active() || !place_pending || event!=2)return 0;
    const bool ok=cviii_lighting_editor_add(x,y)!=0;
    if(ok){place_pending=false;dirty=true;}
    return ok?2:1;
}
extern "C" void cviii_imgui_reset(void){
    place_pending=false;
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
            if(ImGui::Button(place_pending?"PLACE: CLICK SCENE":"Add Light",ImVec2(115,27)))
                place_pending=true;
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
                                  "Subtle\0Steady\0Torch flicker\0"))
                    maybe_change(12,flicker);
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
            ImGui::TextWrapped("Ambient is a scene-wide flat light level. "
                               "Shafts and spot cones remain positioned local lights.");
            ImGui::SeparatorText("Authoring Notes");
            ImGui::BulletText("Lighting only changes final presentation pixels.");
            ImGui::BulletText("Emitters are attached to candidate room IDs.");
            ImGui::BulletText("Geometry-based cast shadows are not yet available.");
            ImGui::BulletText("Lights beyond the screen are culled by their footprint.");
            ImGui::EndTabItem();
        }
        if(ImGui::BeginTabItem("Settings")){
            current_tab=2;
            ImGui::SeparatorText("Global Lighting");
            if(ImGui::Checkbox("Enable all lighting",&enabled))
                maybe_change(0,enabled?1:0);
            int global=model->ambient;
            if(ImGui::SliderInt("Default Ambient",&global,35,100,"%d%%"))
                maybe_change(1,global);
            ImGui::TextWrapped("The default ambient is used in rooms that "
                               "do not have an explicit scene setting.");
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
        place_pending=false;dirty=true;
    }
    if(dirty && !ImGui::IsMouseDown(ImGuiMouseButton_Left)){
        dirty=false;
        return 1; // caller owns existing atomic settings serialization
    }
    return 0;
}
