root=Path(session['workspace']['root']); p=root/'apps/vis-companion/src/lib/attachments.test.ts'; r=await patch(p,[{'from':'11:53b','replace':"import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';"},{'from':'21:dda','replace':"  Capacitor: { isNativePlatform: () => true, convertFileSrc: (path: string) => `native:${path}` },"},{'from':'44:a6f','replace':'''  filePicker.pickImages.mockReset();
});

afterEach(() => vi.unstubAllGlobals());''},{'from':'58:64b','to':'61:a6f','replace':'''    expect(filePicker.pickFiles).toHaveBeenCalledWith({
      types: ['image/png', 'audio/mp4'],
      readData: false,
    });'''}]); print(r)