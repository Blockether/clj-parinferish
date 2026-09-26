root=Path(session["workspace"]["root"]); app=root/"apps/vis-companion/src"
settings=str(app/"screens/SettingsScreen.tsx"); provider=str(app/"components/ProviderAuth.tsx"); machine=str(app/"screens/settings/MachineSettings.tsx"); layout=str(app/"screens/settings/SettingsLayout.tsx"); test=str(app/"components/ui.test.tsx")
print(patch(settings,[{"from":"212:835","to":"216:2c0","replace":"""              /* THE COLUMN'S ONE VERB ENDS ITS BAND AS A BARE MARK. The title already
                 names what the plus adds; a filled disc repeated the same emphasis as
                 the dialog close above it. `edge` spends the header's trailing gutter
                 as hit area and lands the stroke nearer the physical right edge. */"""},{"from":"218:32a","replace":"                variant=\"quiet\"\n                edge"}]))
print(patch(provider,[{"from":"930:583","to":"939:2c6","replace":"""      {/* THE VERB RIDES THE BAND THAT NAMES WHAT IT ADDS. The title supplies the
          noun, so the plus needs neither a word nor a circular face. `edge` extends its
          hit area through the trailing gutter and moves the visible stroke toward the
          panel edge, on the same line as the machine and MCP verbs. */}"""},{"from":"942:f9a","replace":"        variant=\"quiet\"\n        edge"}]))
print(patch(machine,[{"from":"605:bb8","replace":"            variant=\"quiet\"\n            edge"}]))
print(patch(layout,[{"from":"51:1b0","replace":"  /** The column's ONE bare verb, at the physical end of its band. */"},{"from":"57:610","to":"77:612","replace":"""      {/* A BAND NAMES THE COLUMN IN ONE LINE, and its verb is a BARE MARK at the
          physical trailing edge. The title and optional meta wrap in their own cell;
          the action owns the remaining hit area without painting a second object in
          the band. Column and nested-panel bands keep one 36px touch / 32px pointer
          rhythm; their level comes from paper and type, not from a circle around ＋. */}"""},{"from":"121:541","replace":"  /** One bare verb for the whole band, aligned to its physical trailing edge. */"},{"from":"141:ce5","to":"158:4fe","replace":"""      {/* A NESTED BAND IS NOT A COLUMN BAND. It keeps the smaller hint-colour title
          but shares the column band's height and gutter. Its action occupies the
          trailing edge as hit area while the visible plus remains bare, so an action
          neither changes the band's height nor introduces a floating object. */}"""}]))
print(patch(test,[{"from":"1173:3c4","to":"1175:36d","replace":"""  // Regression, Vis session 00000000-0000-4000-8000-000000000021: the three
  // settings pluses were circles sitting one gutter left of the edge."""},{"from":"1189:5de","replace":"    expect(band).toContain('variant=\"quiet\"');\n    expect(band).toContain("edge");"},{"from":"1245:21a","to":"1247:075","replace":"""    // Every add mark is bare and reaches through the band's trailing gutter.
    expect(providerButton).toContain('variant=\"quiet\"');
    expect(providerButton).toContain("edge");
    expect(providerButton).not.toContain('variant=\"primary\"');"""},{"from":"1268:ec9","replace":"    expect(mcp).toContain('variant=\"quiet\"');\n    expect(mcp).toContain("edge");"}]))