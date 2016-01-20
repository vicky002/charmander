import re


def on_message(msg,server):
    text = msg.get("text","")
    match = re.findall(r"~help( .*)?", text)
    if not match:
        return


    help_topic = match[0].strip()
    if help_topic:
        return server.hooks["extendedhelp"].get(help_topic,
                ":fire: no help found for {0}".format(help_topic))
    else:
        help_dir = server.hooks.get("help",{})
        return "\n".join(sorted(help_dir[key]) for key in help_dir)
