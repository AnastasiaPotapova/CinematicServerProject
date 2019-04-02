s = list(input())
k = ''.join([s[x] if (x+1)%2 == 1 else '' for x in range(len(s), -1, -1)])
p = ''.join([s[x] if (x+1)%2 == 0 else '' for x in range(len(s))])
print(p+k)