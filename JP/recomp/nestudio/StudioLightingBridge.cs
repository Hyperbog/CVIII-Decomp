using System.Text;

namespace NEStudio;

public sealed partial class StudioBridge
{
    private string ReadNativeText(long offset,int capacity)
    {
        byte[] bytes=new byte[capacity];
        _view.ReadArray(offset,bytes,0,capacity);
        int zero=Array.IndexOf(bytes,(byte)0);
        return Encoding.ASCII.GetString(bytes,0,zero<0?capacity:zero);
    }

    private StudioLightingSnapshot ReadLightingSnapshot()
    {
        int[] p=new int[18];
        _view.ReadArray(13792,p,0,18);
        var details=new Dictionary<int,StudioLightDetails>();
        for(int i=0;i<128;++i)
        {
            long o=13864L+i*56L;
            details[i]=new StudioLightDetails(i,_view.ReadInt32(o),
                _view.ReadInt32(o+4),_view.ReadInt32(o+8),
                _view.ReadInt32(o+12),_view.ReadInt32(o+16),
                _view.ReadInt32(o+20),ReadNativeText(o+24,32));
        }
        var kits=new List<StudioLightKit>();
        for(int i=0;i<12;++i)
        {
            long o=21032L+i*56L;
            if(_view.ReadInt32(o)==0)continue;
            kits.Add(new StudioLightKit(i,ReadNativeText(o+8,48),
                _view.ReadInt32(o+4)));
        }
        var styles=new List<StudioGlobalStyle>();
        for(int i=0;i<16;++i)
        {
            long o=21704L+i*100L;
            if(_view.ReadInt32(o)==0)continue;
            styles.Add(new StudioGlobalStyle(i,ReadNativeText(o+52,48),
                _view.ReadInt32(o+4),_view.ReadInt32(o+8),
                _view.ReadInt32(o+12),_view.ReadInt32(o+16),
                _view.ReadInt32(o+20),_view.ReadInt32(o+24),
                _view.ReadInt32(o+28),_view.ReadInt32(o+32),
                _view.ReadInt32(o+36),_view.ReadInt32(o+40),
                _view.ReadInt32(o+44),_view.ReadInt32(o+48)));
        }
        var masks=new List<StudioLightMask>();
        for(int i=0;i<64;++i)
        {
            long o=23304L+i*32L;
            if(_view.ReadInt32(o)==0)continue;
            masks.Add(new StudioLightMask(i,_view.ReadInt32(o+4),
                _view.ReadInt32(o+8),_view.ReadInt32(o+12),
                _view.ReadInt32(o+16),_view.ReadInt32(o+20),
                _view.ReadInt32(o+24)));
        }
        var particles=new List<StudioParticle>();
        for(int i=0;i<32;++i)
        {
            long o=25352L+i*116L;
            if(_view.ReadInt32(o)==0)continue;
            particles.Add(new StudioParticle(i,ReadNativeText(o+68,48),
                _view.ReadInt32(o+4),_view.ReadInt32(o+8),
                _view.ReadInt32(o+12),_view.ReadInt32(o+16),
                _view.ReadInt32(o+20),_view.ReadInt32(o+24),
                _view.ReadInt32(o+28),_view.ReadInt32(o+32),
                _view.ReadInt32(o+36),_view.ReadInt32(o+40),
                _view.ReadInt32(o+44),_view.ReadInt32(o+48),
                _view.ReadInt32(o+52),_view.ReadInt32(o+56),
                _view.ReadInt32(o+60),_view.ReadInt32(o+64)));
        }
        var weather=new List<StudioWeather>();
        for(int i=0;i<8;++i)
        {
            long o=29064L+i*104L;
            if(_view.ReadInt32(o)==0)continue;
            weather.Add(new StudioWeather(i,ReadNativeText(o+56,48),
                _view.ReadInt32(o+4),_view.ReadInt32(o+8),
                _view.ReadInt32(o+12),_view.ReadInt32(o+16),
                _view.ReadInt32(o+20),_view.ReadInt32(o+24),
                _view.ReadInt32(o+28),_view.ReadInt32(o+32),
                _view.ReadInt32(o+36),_view.ReadInt32(o+40),
                _view.ReadInt32(o+44),_view.ReadInt32(o+48),
                _view.ReadInt32(o+52)));
        }
        return new StudioLightingSnapshot(p[0],p[1],p[2],p[3],p[4],
            p[5],p[6],p[7],p[8],p[9],p[10],p[11],p[12],
            p[13]!=0,p[14],p[15],p[16]!=0,unchecked((uint)p[17]),
            details,kits,styles,masks,particles,weather);
    }
}
