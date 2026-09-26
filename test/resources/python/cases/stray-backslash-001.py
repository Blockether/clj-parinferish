probe = T / "HlProbe.java"
probe.write_text(r'''
import com.blockether.vis.python.PythonHighlighter;
public class HlProbe {
    public static void main(String[] a) {
        String[] cases = {"x = '''abc\n", "s = '''a\n\nb'''\n", "x = 1\n", "def f(x):\n    return x  # c\n", "\"unterminated\n"};
        for (String c : cases) {
            System.out.println(PythonHighlighter.highlight(c).replace("\u001b", "\\e").replace("\n", "\\n"));
        }
    }
}
''')
sh = await shell(f"cd {T} && java -cp {pkg/'target/classes'} {probe} 2>&1")
print((await sh.wait(60))["out"])
