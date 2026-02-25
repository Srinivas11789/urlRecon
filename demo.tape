# urlRecon — VHS demo tape
# Run with: docker run --rm -v "$PWD":/vhs ghcr.io/charmbracelet/vhs demo.tape
# Or:       make demo

Output samples/urlrecondemo.gif

Set Shell "bash"
Set FontSize 13
Set Width 1100
Set Height 600
Set Theme "Dracula"
Set TypingSpeed 60ms
Set Padding 20

# --- Show help ---
Sleep 500ms
Type "python3 urlrecon/main.py --help"
Sleep 300ms
Enter
Sleep 2s

# --- Clear and run a scan ---
Type "clear"
Enter
Sleep 300ms

Type "python3 urlrecon/main.py -i samples/demo_urls.txt -o /tmp/urlrecon-demo -v"
Sleep 300ms
Enter

# Wait for the three URLs to be processed (DNS + WHOIS + geo + fingerprint)
Sleep 35s

# --- Show the generated output files ---
Type "ls /tmp/urlrecon-demo/report/"
Enter
Sleep 1s

Type "cat /tmp/urlrecon-demo/report/report.txt"
Enter
Sleep 3s

Sleep 2s
