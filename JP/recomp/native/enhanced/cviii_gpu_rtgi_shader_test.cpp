/* ROM-free Windows D3DCompiler gate: compiling C++ is not sufficient
 * to validate the embedded CS5.0 HLSL ray/one-bounce kernel. */
#include <d3dcompiler.h>
#include <cstdio>
#include <cstring>
#include <initializer_list>
#include "cviii_gpu_rtgi_shader_hlsl.h"
#include "cviii_radiance_cascades_shader_hlsl.h"
int main(){
    ID3DBlob *binary=nullptr,*errors=nullptr;
    HRESULT hr=D3DCompile(cviii_gpu_hlsl,std::strlen(cviii_gpu_hlsl),
                          "cviii_gpu_rtgi",nullptr,nullptr,
                          "main","cs_5_0",D3DCOMPILE_OPTIMIZATION_LEVEL3,
                          0,&binary,&errors);
    if(FAILED(hr)){
        std::fprintf(stderr,"CVIII GPU HLSL compile failed: %.*s\n",
            errors?(int)errors->GetBufferSize():0,
            errors?(const char*)errors->GetBufferPointer():"");
        if(errors)errors->Release();
        if(binary)binary->Release();
        return 1;
    }
    if(errors)errors->Release();
    if(!binary || binary->GetBufferSize()<128){
        if(binary)binary->Release();
        std::fprintf(stderr,"CVIII GPU HLSL empty shader output\n");
        return 1;
    }
    std::printf("PASS CVIII GPU shader cs_5_0 (%zu bytes)\n",
                (size_t)binary->GetBufferSize());
    binary->Release();
    for(const char *entry:{"cascadeMain","resolveMain"}){
        ID3DBlob *rc=nullptr,*log=nullptr;
        HRESULT result=D3DCompile(cviii_rc_hlsl,std::strlen(cviii_rc_hlsl),
                                  "cviii_radiance_cascades",nullptr,nullptr,
                                  entry,"cs_5_0",D3DCOMPILE_OPTIMIZATION_LEVEL3,
                                  0,&rc,&log);
        if(FAILED(result) || !rc){
            std::fprintf(stderr,"Radiance Cascades shader %s failed: %.*s\n",
                entry,log?(int)log->GetBufferSize():0,
                log?(const char*)log->GetBufferPointer():"");
            if(log)log->Release();
            if(rc)rc->Release();
            return 1;
        }
        std::printf("PASS Radiance Cascades CS5.0 %s (%zu bytes)\n",
                    entry,(size_t)rc->GetBufferSize());
        if(log)log->Release();
        rc->Release();
    }
    return 0;
}
