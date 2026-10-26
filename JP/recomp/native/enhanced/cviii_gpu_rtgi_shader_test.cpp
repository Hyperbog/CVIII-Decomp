/* ROM-free Windows D3DCompiler gate: compiling C++ is not sufficient
 * to validate the embedded CS5.0 HLSL ray/one-bounce kernel. */
#include <d3dcompiler.h>
#include <cstdio>
#include <cstring>
#include "cviii_gpu_rtgi_shader_hlsl.h"
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
    return 0;
}
