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

namespace {
bool ready=false, place_pending=false, dirty=false;
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

extern "C" int cviii_imgui_event(const SDL_Event *e,SDL_Window *w,SDL_Renderer *r){
    if(!e || !cviii_lighting_editor_active() || !init(w,r))return 0;
    ImGui_ImplSDL2_ProcessEvent(e);
    switch(e->type){
    case SDL_MOUSEBUTTONDOWN:
    case SDL_MOUSEBUTTONUP: {
        const int x=e->button.x,y=e->button.y;
        return within_panel(x,y)||ImGui::GetIO().WantCaptureMouse;
    }
    case SDL_MOUSEMOTION:
        return within_panel(e->motion.x,e->motion.y)||
               ImGui::GetIO().WantCaptureMouse;
    case SDL_MOUSEWHEEL: {
        int x=0,y=0;SDL_GetMouseState(&x,&y);
        return within_panel(x,y)||ImGui::GetIO().WantCaptureMouse;
    }
    case SDL_TEXTINPUT:
        return ImGui::GetIO().WantTextInput;
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
    ImGui::TextColored(ImVec4(.28f,.82f,.91f,1.f),"ENHANCED  /  LIVE EDITOR");
    ImGui::SameLine();
    ImGui::TextDisabled("  HOME: CLOSE");
    ImGui::Separator();

    const CviiiLighting *model=cviii_lighting_editor_model();
    bool enabled=model->enabled!=0;
    if(ImGui::Checkbox("Enable Lighting",&enabled))maybe_change(0,enabled?1:0);
    int ambient=model->ambient;
    ImGui::SetNextItemWidth(-125.f);
    if(ImGui::SliderInt("##Ambient",&ambient,35,100,"%d%%"))maybe_change(1,ambient);
    ImGui::SameLine();
    ImGui::TextUnformatted("Ambient");

    if(ImGui::Button(place_pending?"CLICK SCENE TO PLACE...":"  + Add Light  ",ImVec2(180,31)))
        place_pending=true;
    ImGui::SameLine();
    if(ImGui::Button("Delete Selected",ImVec2(-1,31))){
        if(cviii_lighting_editor_input(5,-1,-1))dirty=true;
    }

    ImGui::SeparatorText("SCENE LIGHTS");
    const unsigned room=cviii_lighting_editor_room();
    if(ImGui::BeginChild("##LightList",ImVec2(0,150),ImGuiChildFlags_Borders)){
        int visible=0;
        for(int i=0;i<CVIII_LIGHT_MAX;++i){
            const CviiiLight &l=model->light[i];
            if(!l.used || l.room!=room)continue;
            ++visible;
            ImGui::PushID(i);
            char name[112];
            std::snprintf(name,sizeof(name),"Light %02d    X %d  Y %d  R %d",i+1,l.x,l.y,l.radius);
            if(ImGui::Selectable(name,model->selected==i)){
                (void)cviii_lighting_editor_select(i);
            }
            ImGui::PopID();
        }
        if(!visible)ImGui::TextDisabled("No lights in this room. Click Add Light.");
    }
    ImGui::EndChild();

    const int selected=model->selected;
    if(selected>=0 && selected<CVIII_LIGHT_MAX &&
       model->light[selected].used && model->light[selected].room==room){
        const CviiiLight &light=model->light[selected];
        ImGui::SeparatorText("LIGHT PROPERTIES");
        ImGui::Text("Light %02d     World position  X: %d   Y: %d",
                    selected+1,light.x,light.y);
        int radius=light.radius,energy=light.energy;
        if(ImGui::SliderInt("Radius",&radius,12,160,"%d px"))maybe_change(2,radius);
        if(ImGui::SliderInt("Intensity",&energy,5,160,"%d"))maybe_change(3,energy);
        float rgb[3]={light.red/255.f,light.green/255.f,light.blue/255.f};
        if(ImGui::ColorEdit3("Light Color",rgb,
            ImGuiColorEditFlags_PickerHueWheel|ImGuiColorEditFlags_DisplayRGB)){
            maybe_change(4,(int)(rgb[0]*255.f+0.5f));
            maybe_change(5,(int)(rgb[1]*255.f+0.5f));
            maybe_change(6,(int)(rgb[2]*255.f+0.5f));
        }
        if(ImGui::Button("Warm Candle")){
            maybe_change(4,255);maybe_change(5,167);maybe_change(6,74);
        }
        ImGui::SameLine();
        if(ImGui::Button("Cold Blue")){
            maybe_change(4,150);maybe_change(5,196);maybe_change(6,255);
        }
        ImGui::SameLine();
        if(ImGui::Button("White")){
            maybe_change(4,255);maybe_change(5,255);maybe_change(6,255);
        }
        ImGui::TextDisabled("Drag the center handle on the game to move this light.");
    }else{
        ImGui::SeparatorText("LIGHT PROPERTIES");
        ImGui::TextDisabled("Select a light from the list to edit it.");
    }
    ImGui::Separator();
    ImGui::TextDisabled("Room: %08X   |  Ctrl+Home: Remap Editor Key",room);
    if(ImGui::Button("Resume Game",ImVec2(-1,31)))stay_open=false;
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
