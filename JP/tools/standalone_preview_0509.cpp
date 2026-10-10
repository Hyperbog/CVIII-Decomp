#include "standalone_scene_0509.hpp"
#include <charconv>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string_view>

int main(int argc,char** argv){
    try{
        if(argc!=4)throw std::invalid_argument("Usage: cviii-standalone-preview FRAMES INPUT_PATTERN OUT.ppm; input R=right L=left J=jump X=remove enemy .=idle");
        unsigned frames=0;
        std::string_view arg(argv[1]);
        const auto result=std::from_chars(arg.data(),arg.data()+arg.size(),frames);
        if(result.ec!=std::errc{}||result.ptr!=arg.data()+arg.size()||frames>10000)
            throw std::invalid_argument("FRAMES must be a decimal integer <=10000");
        const std::string_view keys(argv[2]);
        if(keys.empty())throw std::invalid_argument("empty demonstration input pattern");
        cv3::StandaloneScene0509 scene;
        for(unsigned i=0;i<frames;++i){
            std::uint8_t buttons=0;
            switch(keys[i%keys.size()]){
                case '.':break;
                case 'R':buttons=cv3::StandaloneScene0509::Right;break;
                case 'L':buttons=cv3::StandaloneScene0509::Left;break;
                case 'J':buttons=cv3::StandaloneScene0509::Jump;break;
                case 'X':buttons=cv3::StandaloneScene0509::RemoveEnemy;break;
                default:throw std::invalid_argument("input accepts only R,L,J,X,.");
            }
            scene.step(buttons);
        }
        auto pixels=scene.render_rgb();
        std::ofstream file(argv[3],std::ios::binary|std::ios::trunc);
        if(!file)throw std::runtime_error("failed to open output PPM");
        file<<"P6\n"<<cv3::StandaloneScene0509::kWidth<<" "<<cv3::StandaloneScene0509::kHeight<<"\n255\n";
        file.write(reinterpret_cast<const char*>(pixels.data()),std::streamsize(pixels.size()));
        if(!file)throw std::runtime_error("failed to write PPM");
        std::cout<<"ROM_INDEPENDENT_SYNTHETIC_PREVIEW frames="<<scene.frame()
                 <<" x="<<unsigned(scene.player_x())<<" y="<<unsigned(scene.player_y())
                 <<" enemy="<<(scene.enemy_present()?1:0)
                 <<" near_contact_frames="<<scene.near_contact_frames()
                 <<" image_fnv64="<<std::hex<<std::setw(16)<<std::setfill('0')
                 <<cv3::StandaloneScene0509::fnv1a64(pixels)<<"\n";
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 2;}
}
