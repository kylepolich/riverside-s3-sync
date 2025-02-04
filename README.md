# Riverside S3 Sync

In late 2024 Riverside made some change that broke the ability to easily download our recordings in a programmatic way.  They offer an API but wanted to charge hundreds of dollars for access!

If you're in the same bind as we were, please use this open-source script that will use browser automation to enable you to access your data in a reasonable way.

This script copies all your recent recordings to your own S3 bucket.  It only does the copy if the file doesn't already exist so you don't re-download each time.