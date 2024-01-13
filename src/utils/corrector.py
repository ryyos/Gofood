
def vname(name: str) -> str:
  invalid_chars = [')','(','/', '\\', ':', '*', '?', '"', '-', '<', '>', '|', '+', '=', '%', '@', '#', '$', '^', '[', ']', '{', '}', '`', '~', '<', '>', '#', '%', '{', '}', '|', '\\', '^', '~', '[', ']', '`', ';', '/', '?', ':', '@', '=', "'", ",", "."]

  valid = ''.join(char if char not in invalid_chars else '' for char in name)

  return valid.replace(" ", "-").replace('&', '-').replace("--", "-")

def file_name(name: str) -> str:
    invalid_chars = [')','(','/', '\\', ':', '*', '?', '"', '-', '<', '>', '|', '+', '=', '&', '%', '@', '#', '$', '^', '[', ']', '{', '}', '`', '~', '<', '>', '#', '%', '{', '}', '|', '\\', '^', '~', '[', ']', '`', ';', '/', '?', ':', '@', '=', '&', "'", ",", "."]
    falid = ''.join(char if char not in invalid_chars else '' for char in name)
    
    return falid.replace(" ", "_")


if __name__ == '__main__':
  print(vname("A&W, Linc Square"))