> 
# Compare the four iteration end-arrow rows in the TUI.
for m in re.finditer(r'<div class="tln"><span aria-hidden="true" class="r">[^\n]*ar[^\n]*</div>', html):
    print(m.start(), repr(m.group(0)))
print('--- corrupted sites ---')
for pos in (75762, 84162):
    print(repr(html[pos-260:pos+120]))
    print('===')
