# cogwheel.py
import re

class CogWheel:
    def __init__(self, filepath=None):
        self.filepath = filepath
        self.data = {}  # {section: {key: value}}
        self.comments = {}  # {section: {key: comment}}
        self.section_order = []  # preserve section order
        if filepath:
            self.load(filepath)

    def parse_value(self, value):
        """Convert string to proper type."""
        value = value.strip()
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
        elif re.match(r"^-?\d+$", value):
            return int(value)
        elif re.match(r"^-?\d+\.\d+$", value):
            return float(value)
        elif value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        else:
            return value  # fallback as string

    def load(self, filepath):
        current_section = None
        self.data = {}
        self.comments = {}
        self.section_order = []
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            line = line.rstrip()
            if not line.strip():
                continue  # skip empty lines
            if line.strip().startswith("//"):
                # store comment for the next key
                last_comment = line.strip()
                continue
            if line.startswith("[") and line.endswith("]"):
                current_section = line[1:-1].strip()
                self.section_order.append(current_section)
                self.data[current_section] = {}
                self.comments[current_section] = {}
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                # check for inline comment
                if "//" in value:
                    value_part, comment = value.split("//", 1)
                    value = value_part.strip()
                    comment = "//" + comment.strip()
                else:
                    comment = last_comment if 'last_comment' in locals() else ""
                parsed_value = self.parse_value(value)
                section = current_section or "DEFAULT"
                if section not in self.data:
                    self.data[section] = {}
                    self.comments[section] = {}
                    self.section_order.append(section)
                self.data[section][key] = parsed_value
                self.comments[section][key] = comment
                if 'last_comment' in locals():
                    del last_comment

    def get(self, key, section=None):
        section = section or "DEFAULT"
        return self.data.get(section, {}).get(key)

    def set(self, key, value, section=None):
        section = section or "DEFAULT"
        if section not in self.data:
            self.data[section] = {}
            self.comments[section] = {}
            self.section_order.append(section)
        self.data[section][key] = value

    def save(self, filepath=None):
        filepath = filepath or self.filepath
        if not filepath:
            raise ValueError("Filepath is not set.")

        lines = []
        for section in self.section_order:
            if section != "DEFAULT":
                lines.append(f"[{section}]")
            for key, value in self.data[section].items():
                # convert Python value to string
                if isinstance(value, bool):
                    value_str = "true" if value else "false"
                elif isinstance(value, (int, float)):
                    value_str = str(value)
                else:
                    value_str = f'"{value}"'
                comment = self.comments[section].get(key, "")
                line = f"{key} = {value_str}"
                if comment:
                    line += " " + comment
                lines.append(line)
            lines.append("")  # empty line after section
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

# ===== Example Usage =====
if __name__ == "__main__":
    config = CogWheel("settings.cog")
    print(config.get("current_mode"))  # read value
    config.set("current_mode", 2)      # modify value
    config.set("new_option", True, "Experimental")  # add to section
    config.save()  # save changes back
