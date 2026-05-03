# Dependency Cleanup / Audit Commands

Run these from the Lambda source folder if you are maintaining the Node.js package locally.

```bash
# Show known dependency issues
npm audit

# Remove the vulnerable package if it is no longer needed
npm uninstall node-serialize

# Reinstall dependencies after package changes
npm install

# Review final dependency tree
npm ls
```

The application fix is not only running `npm audit`; the important change is removing unsafe deserialization from the request path and replacing it with safe JSON parsing.
