import ldap

# Initialize LDAP connection
conn = ldap.initialize('ldap://ldap.uchicago.edu:389')

# Anonymous bind (UChicago LDAP allows this)
conn.simple_bind_s()


# Exercise 1 Find Yourself
search_base = "ou=People,dc=uchicago,dc=edu"
search_filter = "katherinezh"  # Replace 'Your Name' with your actual name

result = conn.search_s(search_base, ldap.SCOPE_SUBTREE, search_filter)

for dn, entry in result:
    print(f"DN: {dn}")
    for attr, values in entry.items():
        print(f"{attr}: {values}")

# Exercise 2 Get only name, department, and email
search_filter = "(cn=Your Name)"  # Replace with your name
attributes = ['cn', 'ou', 'mail']  # Common attributes for name, department, and email

result = conn.search_s(search_base, ldap.SCOPE_SUBTREE, search_filter, attributes)

for dn, entry in result:
    print(f"DN: {dn}")
    for attr in attributes:
        print(f"{attr}: {entry.get(attr, 'Not Found')}")

#Exercise 3: Find a List of (Max 10) People in the Department
search_base = "ou=People,dc=uchicago,dc=edu"
search_filter = "(ou=Computer Science)"  # Modify as needed

id = conn.search_ext(search_base, ldap.SCOPE_SUBTREE, search_filter, sizelimit=10)

while True:
    rtype, rdata, rid = conn.result(id, 0)
    if not rdata:
        break

    for dn, entry in rdata:
        print(f"DN: {dn}")
        print(f"Name: {entry.get('cn', ['Unknown'])}")
        print(f"Email: {entry.get('mail', ['No Email'])}")
        print("-----------")
