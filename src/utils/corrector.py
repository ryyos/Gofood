
def vname(name: str) -> str:
  alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'
             ,'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
             '1','2','3','4','5','6','7','8','9','0', '_']

  valid = ''.join(char if char in alphabet else '-' for char in name)

  return valid.lower().replace(" ", "-").replace("--", "-").replace("---", "-")

def file_name(name: str) -> str:
    invalid_chars = [')','(','/', '\\', ':', '*', '?', '"', '-', '<', '>', '|', '+', '=', '&', '%', '@', '#', '$', '^', '[', ']', '{', '}', '`', '~', '<', '>', '#', '%', '{', '}', '|', '\\', '^', '~', '[', ']', '`', ';', '/', '?', ':', '@', '=', '&', "'", ",", "."]
    falid = ''.join(char if char not in invalid_chars else '' for char in name)
    
    return falid.replace(" ", "_")


if __name__ == '__main__':
  print(vname("Bakmi & Seafood 99, Kemang Pratama"))