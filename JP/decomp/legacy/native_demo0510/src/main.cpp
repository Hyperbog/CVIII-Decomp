// CVIII JP native first-stage experience prototype.
// No 6502 interpreter, embedded ROM, mapper, NES sound driver or Mesen runtime.
// Backgrounds/sprite from private original-ROM emulator reference stills;
// physics, player and transitions are host-side provisional gameplay.
#include <algorithm>
#include <array>
#include <cctype>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>
#ifdef _WIN32
#define NOMINMAX
#include <windows.h>
#else
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/keysym.h>
#endif

namespace cv3 {
constexpr int W=256,H=240;
using Frame=std::vector<std::uint32_t>;
struct Art{
 Frame title=Frame(W*H),intro=Frame(W*H),stage=Frame(W*H);
 std::array<std::uint8_t,25*34*4> player{};
 bool loaded=false;
};
static std::uint32_t color(unsigned r,unsigned g,unsigned b){return (r<<16)|(g<<8)|b;}
static bool ppm(const std::string& path,Frame& dst){
 std::ifstream f(path,std::ios::binary);if(!f)return false;
 std::string mag;int w=0,h=0,maxc=0;f>>mag>>w>>h>>maxc;
 if(mag!="P6" || w!=W || h!=H || maxc!=255)return false;
 f.get();std::vector<unsigned char> bytes(W*H*3);
 f.read(reinterpret_cast<char*>(bytes.data()),static_cast<std::streamsize>(bytes.size()));
 if(!f)return false;
 for(size_t i=0;i<dst.size();++i)dst[i]=color(bytes[i*3],bytes[i*3+1],bytes[i*3+2]);
 return true;
}
static bool loadArt(const std::string& path,Art& a){
 bool ok=ppm(path+"/title.ppm",a.title)&ppm(path+"/intro.ppm",a.intro)&ppm(path+"/stage.ppm",a.stage);
 std::ifstream f(path+"/player.rgba",std::ios::binary);
 if(f){f.read(reinterpret_cast<char*>(a.player.data()),static_cast<std::streamsize>(a.player.size()));ok &= bool(f);}else ok=false;
 a.loaded=ok;return ok;
}
static void rectangle(Frame& f,int x,int y,int w,int h,std::uint32_t c){
 for(int j=std::max(0,y);j<std::min(H,y+h);++j)
   for(int i=std::max(0,x);i<std::min(W,x+w);++i) f[static_cast<size_t>(j)*W+i]=c;
}
// Small true bitmap font for overlay, not derived from game CHR/ROM.
static constexpr const char* glyph(char c){
 switch(c){
 case 'A':return "01110100011000111111100011000110001";
 case 'B':return "11110100011000111110100011000111110";
 case 'C':return "01111100001000010000100001000001111";
 case 'D':return "11110100011000110001100011000111110";
 case 'E':return "11111100001000011110100001000011111";
 case 'F':return "11111100001000011110100001000010000";
 case 'G':return "01111100001000010111100011000101111";
 case 'H':return "10001100011000111111100011000110001";
 case 'I':return "11111001000010000100001000010011111";
 case 'J':return "00111000100001000010100101001001100";
 case 'K':return "10001100101010011000101001001010001";
 case 'L':return "10000100001000010000100001000011111";
 case 'M':return "10001110111010110101100011000110001";
 case 'N':return "10001110011010110011100011000110001";
 case 'O':return "01110100011000110001100011000101110";
 case 'P':return "11110100011000111110100001000010000";
 case 'Q':return "01110100011000110001101011001001101";
 case 'R':return "11110100011000111110101001001010001";
 case 'S':return "01111100001000001110000011000111110";
 case 'T':return "11111001000010000100001000010000100";
 case 'U':return "10001100011000110001100011000101110";
 case 'V':return "10001100011000110001100010101000100";
 case 'W':return "10001100011000110101101011101110001";
 case 'X':return "10001100010101000100010101000110001";
 case 'Y':return "10001100010101000100001000010000100";
 case 'Z':return "11111000010001000100010001000011111";
 case '0':return "01110100011001110101110011000101110";
 case '1':return "00100011000010000100001000010001110";
 case '2':return "01110100010000100010001000100011111";
 case '3':return "11110000010000101110000010000111110";
 case '4':return "00010001100101010010111110001000010";
 case '5':return "11111100001111000001000011000101110";
 case '6':return "00111010001000011110100011000101110";
 case '7':return "11111000010001000100010000100001000";
 case '8':return "01110100011000101110100011000101110";
 case '9':return "01110100011000101111000010001011100";
 case ':':return "00000001000010000000001000010000000";
 case '-':return "00000000000000011111000000000000000";
 case '.':return "00000000000000000000000000010000100";
 case '/':return "00001000010001000100010001000000000";
 case '!':return "00100001000010000100001000000000100";
 case '>':return "10000010000010000010010001000000000";
 default:return "00000000000000000000000000000000000";
 }
}
static void print(Frame& f,int x,int y,const std::string& text,std::uint32_t c,int scale=1){
 for(char t:text){const char* b=glyph(static_cast<char>(std::toupper(static_cast<unsigned char>(t))));
  for(int r=0;r<7;++r)for(int k=0;k<5;++k)if(b[r*5+k]=='1')
    rectangle(f,x+k*scale,y+r*scale,scale,scale,c);
  x+=6*scale;
 }
}
// Source-verified fixed $FF06 vacancy preference, lifted into native host RAM.
// This does not imply that original player/AI movement is reconstructed.
static unsigned firstVacant(const std::array<std::uint8_t,2048>& ram){
 for(unsigned x=1;x<=12;++x)if(ram[0x054e + x]==0)return x;
 return 13;
}
static void clear18(std::array<std::uint8_t,2048>& ram,unsigned x){
 constexpr std::array<unsigned,18> fields{0x04f2,0x0509,0x0520,0x0537,
  0x067b,0x068d,0x0454,0x0470,0x0565,0x04c4,0x04db,0x05c1,0x05d8,0x05ef,0x0606,0x061d,0x0633,0x0645};
 for(unsigned base:fields)ram[(base+x)&0x7ff]=0;
}
struct Input {bool left=false,right=false,jump=false,attack=false,enter=false,escape=false,restart=false;};
class Game {
public:
 Game(){reset();}
 enum class Scene{Title,Intro,Stage,Complete};
 Scene scene=Scene::Title;
 int frames=0,phase=0,scroll=0,hits=0;
 float x=34.f,y=174.f,vy=0.f;
 bool grounded=true,enemyAlive=true,flip=false;
 bool stageVisited=false;
 std::array<std::uint8_t,2048> ram{};
 void reset(){scene=Scene::Title;frames=phase=scroll=hits=0;x=34;y=174;vy=0;grounded=true;enemyAlive=true;flip=false;stageVisited=false;ram.fill(0);ram[0x054f]=0x3d;}
 void tick(const Input& in){
  if(in.restart){reset();return;}
  ++frames;++phase;
  if(scene==Scene::Title){if(in.enter){scene=Scene::Intro;phase=0;}return;}
  if(scene==Scene::Intro){if(in.enter||phase>=420){scene=Scene::Stage;phase=0;stageVisited=true;}return;}
  if(scene==Scene::Complete){if(in.enter)reset();return;}
  // Demonstrator host movement -- not yet the original character state machine.
  int dx=int(in.right)-int(in.left);
  if(dx){x+=float(dx)*1.45f;x=std::clamp(x,4.f,242.f);flip=dx<0;}
  if(in.jump && grounded){vy=-5.5f;grounded=false;}
  if(!grounded){y+=vy;vy+=.26f;}
  // Single-room temporary floor geometry. Real stage metatile collision is OPEN.
  float floor=174.f;
  if(x>170.f&&x<210.f)floor=160.f;
  if(y>=floor){y=floor;vy=0;grounded=true;}
  if(enemyAlive && in.attack && (phase%12==0)){
   if(std::abs(x-111.f)<63.f && std::abs(y-174.f)<48.f){
    clear18(ram,1);ram[0x054f]=0;enemyAlive=false;++hits;
   }
  }
  if(x>238.f){scene=Scene::Complete;phase=0;}
 }
 static void sprite(Frame& f,const Art& a,int xx,int yy,bool mirrored){
  for(int y0=0;y0<34;++y0)for(int x0=0;x0<25;++x0){
    int sx=mirrored?24-x0:x0;
    size_t i=(static_cast<size_t>(y0)*25+sx)*4;
    if(a.player[i+3]&&xx+x0>=0&&xx+x0<W&&yy+y0>=0&&yy+y0<H)
      f[static_cast<size_t>(yy+y0)*W+xx+x0]=color(a.player[i],a.player[i+1],a.player[i+2]);
  }
 }
 Frame render(const Art& a)const{
  Frame out=(scene==Scene::Title || (scene==Scene::Intro && phase<160))?a.title:
            (scene==Scene::Intro?a.intro:a.stage);
  constexpr auto ivory=0xffead0u, peach=0xfe8170u,grey=0xb0b0b0u;
  if(scene==Scene::Title){
   rectangle(out,12,11,232,100,0x070919);
   rectangle(out,17,16,222,90,0x111329);
   print(out,41,32,"AKUMAJOU",peach,2);
   print(out,47,55,"DENSETSU",ivory,2);
   print(out,54,84,"NATIVE PC DEMO",grey);
   print(out,34,205,"ENTER TO BEGIN",ivory);
  }else if(scene==Scene::Intro){
   rectangle(out,0,0,256,26,0x090915);
   print(out,9,8,"THE LEGEND BEGINS",ivory);
   if(phase<160)print(out,50,205,"TRANSYLVANIA",peach);
   else print(out,37,202,"THE ROAD AWAITS",ivory);
   if((phase/35)%2==0)print(out,43,224,"ENTER TO SKIP",peach);
  }else if(scene==Scene::Stage){
   rectangle(out,0,0,256,42,0x000000);
   print(out,4,4,"STAGE 1  PC PROTOTYPE",ivory);
   print(out,4,15,"ARROWS MOVE Z JUMP X HIT",grey);
   if(enemyAlive){
    // temporary native enemy visual (not an original AI model)
    rectangle(out,110,180,12,21,0x05130a);
    rectangle(out,113,177,7,9,0x48cdde);
    rectangle(out,112,193,11,6,0x0c9300);
   }
   sprite(out,a,int(x),int(y),flip);
   if((phase%12)<4 && !grounded)rectangle(out,int(x)+10,int(y)-2,3,3,ivory);
   if((phase%12)<4 && hits)print(out,183,31,"HIT",peach);
   print(out,4,230,"R RESET  ESC QUIT",grey);
  }else{
   rectangle(out,15,57,226,121,0x000000);
   print(out,38,76,"STAGE 1 DEMO",peach,2);
   print(out,54,109,"COMPLETE",ivory,2);
   print(out,30,150,"ENTER TO RESTART",grey);
  }
  return out;
 }
};

static void ppmSave(const std::string& filename,const Frame& src){
 std::ofstream f(filename,std::ios::binary);if(!f)throw std::runtime_error("Cannot write output: "+filename);
 f<<"P6\n256 240\n255\n";
 for(std::uint32_t c:src){char rgb[]{char((c>>16)&255),char((c>>8)&255),char(c&255)};f.write(rgb,3);}
}
static std::uint64_t hash(const Frame& f){std::uint64_t h=0xcbf29ce484222325ull;
 for(auto c:f){for(int k=0;k<3;++k){h^=(c>>(16-k*8))&255;h*=0x100000001b3ull;}}
 return h;}
static bool test(Game& g){
 g.reset();g.tick(Input{.enter=true});if(g.scene!=Game::Scene::Intro)return false;
 g.tick(Input{.enter=true});if(g.scene!=Game::Scene::Stage||!g.stageVisited)return false;
 float px=g.x;for(int j=0;j<30;++j)g.tick(Input{.right=true});if(g.x<=px+30.f)return false;
 float py=g.y;g.tick(Input{.jump=true});if(g.y>=py)return false;
 for(int j=0;j<110;++j)g.tick(Input{});
 if(!g.grounded)return false;
 if(firstVacant(g.ram)!=2)return false;
 for(int j=0;j<40;++j)g.tick(Input{.right=true,.attack=true});
 if(g.enemyAlive||g.ram[0x054f]!=0||firstVacant(g.ram)!=1)return false;
 for(int j=0;j<130;++j)g.tick(Input{.right=true});
 if(g.scene!=Game::Scene::Complete)return false;
 g.tick(Input{.enter=true});return g.scene==Game::Scene::Title;
}
}

#ifndef _WIN32
static int windowRun(cv3::Game& game,const cv3::Art& art,int scale,int smokeFrames=0){
 Display* d=XOpenDisplay(nullptr);if(!d){std::cerr<<"No X11 display; use --headless.\n";return 4;}
 const int sw=cv3::W*scale,sh=cv3::H*scale;
 Window w=XCreateSimpleWindow(d,DefaultRootWindow(d),100,80,sw,sh,0,0,0);
 XStoreName(d,w,"Akumajou Densetsu - Native PC Prototype (0509)");
 XSelectInput(d,w,ExposureMask|KeyPressMask|KeyReleaseMask|StructureNotifyMask);
 Atom destroy=XInternAtom(d,"WM_DELETE_WINDOW",False);XSetWMProtocols(d,w,&destroy,1);
 XMapWindow(d,w);GC gc=XCreateGC(d,w,0,nullptr);
 auto* visual=DefaultVisual(d,DefaultScreen(d));
 auto* image=XCreateImage(d,visual,DefaultDepth(d,DefaultScreen(d)),ZPixmap,0,
        static_cast<char*>(std::calloc(static_cast<size_t>(sw)*sh,4)),sw,sh,32,0);
 if(!image){XFreeGC(d,gc);XDestroyWindow(d,w);XCloseDisplay(d);return 3;}
 std::array<bool,8> key{};auto next=std::chrono::steady_clock::now();bool running=true;int presented=0;
 while(running){
  while(XPending(d)){
   XEvent e{};XNextEvent(d,&e);
   if(e.type==ClientMessage && static_cast<Atom>(e.xclient.data.l[0])==destroy){running=false;break;}
   if(e.type!=KeyPress&&e.type!=KeyRelease)continue;
   KeySym sym=XLookupKeysym(&e.xkey,0);
   int idx=-1;
   switch(sym){case XK_Left:case XK_a:idx=0;break;case XK_Right:case XK_d:idx=1;break;
     case XK_Up:case XK_z:case XK_space:idx=2;break;case XK_x:idx=3;break;
     case XK_Return:idx=4;break;case XK_r:idx=5;break;case XK_Escape:idx=6;break;
     default:break;}
   if(idx>=0)key[static_cast<size_t>(idx)]=e.type==KeyPress;
  }
  if(key[6])running=false;
  cv3::Input in{};in.left=key[0];in.right=key[1];in.jump=key[2];in.attack=key[3];
  in.enter=key[4];in.restart=key[5];
  game.tick(in);
  // Consume one-shot scene buttons; key-repeat should not skip both screens.
  key[4]=false;key[5]=false;
  const auto f=game.render(art);
  for(int y=0;y<cv3::H;++y)for(int x=0;x<cv3::W;++x){
   const auto rgb=f[static_cast<size_t>(y)*cv3::W+x];
   for(int j=0;j<scale;++j)for(int i=0;i<scale;++i){
    // 24-bit TrueColor visual assumption; runs on normal desktop X11/Xvfb.
    XPutPixel(image,x*scale+i,y*scale+j,rgb);
   }
  }
  XPutImage(d,w,gc,image,0,0,0,0,sw,sh);XFlush(d);
  if(smokeFrames>0 && ++presented>=smokeFrames)running=false;
  next+=std::chrono::milliseconds(16);
  std::this_thread::sleep_until(next);
 }
 XDestroyImage(image);XFreeGC(d,gc);XDestroyWindow(d,w);XCloseDisplay(d);return 0;
}
#else
static cv3::Input inWin(){cv3::Input i{};
 i.left=(GetAsyncKeyState(VK_LEFT)&0x8000)!=0 || (GetAsyncKeyState('A')&0x8000)!=0;
 i.right=(GetAsyncKeyState(VK_RIGHT)&0x8000)!=0 || (GetAsyncKeyState('D')&0x8000)!=0;
 i.jump=(GetAsyncKeyState('Z')&0x8000)!=0 || (GetAsyncKeyState(VK_UP)&0x8000)!=0;
 i.attack=(GetAsyncKeyState('X')&0x8000)!=0;
 i.enter=(GetAsyncKeyState(VK_RETURN)&0x8000)!=0;
 i.restart=(GetAsyncKeyState('R')&0x8000)!=0;
 i.escape=(GetAsyncKeyState(VK_ESCAPE)&0x8000)!=0;return i;}
static int windowRun(cv3::Game& game,const cv3::Art& art,int scale,int smokeFrames=0){
 auto name=L"Akumajou Densetsu - Native PC Prototype";
 HINSTANCE app=GetModuleHandleW(nullptr);
 WNDCLASSW wc{};wc.lpfnWndProc=DefWindowProcW;wc.hInstance=app;wc.lpszClassName=L"CVIIIJPHost0509";
 RegisterClassW(&wc);
 HWND h=CreateWindowW(wc.lpszClassName,name,WS_OVERLAPPEDWINDOW|WS_VISIBLE,100,100,
 cv3::W*scale+16,cv3::H*scale+39,nullptr,nullptr,app,nullptr);
 if(!h)return 2;
 BITMAPINFO bmi{};bmi.bmiHeader.biSize=sizeof(BITMAPINFOHEADER);
 bmi.bmiHeader.biWidth=cv3::W;bmi.bmiHeader.biHeight=-cv3::H;
 bmi.bmiHeader.biPlanes=1;bmi.bmiHeader.biBitCount=32;bmi.bmiHeader.biCompression=BI_RGB;
 std::vector<std::uint32_t> bgr(cv3::W*cv3::H);
 auto t=std::chrono::steady_clock::now();bool previousEnter=false,previousReset=false;int presented=0;
 while(IsWindow(h)){
  MSG msg{};while(PeekMessageW(&msg,nullptr,0,0,PM_REMOVE)){
   if(msg.message==WM_QUIT){DestroyWindow(h);return 0;}
   TranslateMessage(&msg);DispatchMessageW(&msg);
  }
  auto in=inWin();if(in.escape){DestroyWindow(h);break;}
  bool nowEnter=in.enter,nowReset=in.restart;
  in.enter=nowEnter&&!previousEnter;in.restart=nowReset&&!previousReset;
  previousEnter=nowEnter;previousReset=nowReset;
  game.tick(in);auto frame=game.render(art);
  std::copy(frame.begin(),frame.end(),bgr.begin());
  HDC dc=GetDC(h);RECT rc{};GetClientRect(h,&rc);
  const int blit=StretchDIBits(dc,0,0,rc.right,rc.bottom,0,0,cv3::W,cv3::H,
    bgr.data(),&bmi,DIB_RGB_COLORS,SRCCOPY);ReleaseDC(h,dc);
  if(blit==GDI_ERROR || blit==0){DestroyWindow(h);std::cerr<<"GDI StretchDIBits failure\n";return 5;}
  if(smokeFrames>0 && ++presented>=smokeFrames){DestroyWindow(h);std::cout<<"PASS Windows GDI window "<<presented<<" frames\n";return 0;}
  t+=std::chrono::milliseconds(16);std::this_thread::sleep_until(t);
 }return 0;
}
#endif
int main(int argc,char** argv){
 try{
  std::string assets="assets",script="",scene="title",output="";bool headless=false,selftest=false,windowtest=false;
  int frames=0,scale=3;
  for(int i=1;i<argc;++i){
   const std::string a=argv[i];
   auto arg=[&](){if(i+1>=argc)throw std::runtime_error("Missing option value "+a);return std::string(argv[++i]);};
   if(a=="--assets")assets=arg();else if(a=="--frames")frames=std::stoi(arg());
   else if(a=="--scale")scale=std::stoi(arg());else if(a=="--scene")scene=arg();
   else if(a=="--script")script=arg();else if(a=="--output")output=arg();
   else if(a=="--headless")headless=true;else if(a=="--self-test")selftest=true;
   else if(a=="--window-test")windowtest=true;
   else if(a=="--help"){
    std::cout<<"CVIII JP native PC preview (not full game parity)\n"
             <<"--assets DIR --headless --scene title|intro|stage --frames N --script TEXT --output screenshot.ppm\n"
             <<"Keys: Enter begin/skip, arrows or A/D move, Z jump, X attack, R restart, Esc quit\n";return 0;
   }else throw std::runtime_error("Unknown argument: "+a);
  }
  cv3::Game g;if(selftest){if(!cv3::test(g)){std::cerr<<"Native stage machine self-test FAIL\n";return 2;}std::cout<<"PASS  native scene transitions, movement, jump, actor allocation, attack, stage exit\n";return 0;}
  cv3::Art art;if(!cv3::loadArt(assets,art))throw std::runtime_error("Missing private stage preview assets in "+assets);
  if(scale<1||scale>5)throw std::runtime_error("Scale must be 1..5");
  if(!headless)return windowRun(g,art,scale,windowtest?120:0);
  if(frames<0||frames>30000)throw std::runtime_error("Frames out of range");
  if(scene=="intro"){g.scene=cv3::Game::Scene::Intro;g.phase=0;}
  else if(scene=="stage"){g.scene=cv3::Game::Scene::Stage;g.stageVisited=true;g.phase=0;}
  else if(scene!="title")throw std::runtime_error("Invalid scene");
  for(int j=0;j<frames;++j){const char ch=script.empty()?'.':script[static_cast<size_t>(j)%script.size()];
   cv3::Input in{};in.enter=ch=='e';in.right=ch=='r';in.left=ch=='l';
   in.jump=ch=='j';in.attack=ch=='x';in.restart=ch=='R';g.tick(in);
  }
  const auto f=g.render(art);if(!output.empty())cv3::ppmSave(output,f);
  std::cout<<"Native frame="<<g.frames<<" scene="<<static_cast<int>(g.scene)
           <<" x="<<g.x<<" y="<<g.y<<" hits="<<g.hits
           <<" enemy_alive="<<g.enemyAlive<<" RGB_FNV64="<<std::hex<<cv3::hash(f)<<std::dec<<"\n";
  return 0;
 }catch(const std::exception& e){std::cerr<<"Error: "<<e.what()<<"\n";
#ifdef _WIN32
  MessageBoxA(nullptr,e.what(),"CVIII JP native demo error",MB_OK|MB_ICONERROR);
#endif
  return 1;}
}
