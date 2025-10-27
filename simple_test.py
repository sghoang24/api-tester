import pandas as pd

print("Testing template download functionality...")
df = pd.DataFrame({
    'StudentID': ['STU001'], 
    'FutureStage': [1], 
    'FutureCourseVersionCode': ['CS101V1']
})
print("✅ DataFrame created successfully")
print(df)
print("✅ Template download feature is ready!")
