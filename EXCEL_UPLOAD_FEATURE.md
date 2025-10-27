# Excel Upload Feature for AD Module APIs

## Overview

This feature adds Excel file upload functionality specifically for Administration (AD) module APIs, particularly for the `DEVEXUpdateStudentUser` API.

## Key Features

### 1. **Conditional Display**

- Only appears for AD module APIs containing "DEVEXUpdateStudentUser" in the name
- Replaces the standard JSON editor with an enhanced Excel upload interface

### 2. **Excel File Processing**

- Accepts `.xlsx` and `.xls` file formats
- Validates required columns: `StudentID`, `FutureStage`, `FutureCourseVersionCode`
- Shows data preview before processing
- Converts Excel data to proper JSON format

### 3. **Data Validation**

- Checks for required columns
- Shows preview of uploaded data (first 10 rows)
- Displays total record count
- Validates data types during conversion

### 4. **JSON Generation**

The uploaded Excel data is converted to this JSON structure:

```json
{
  "students": [
    {
      "studentId": "e9cd949a-1272-4e00-9160-431e69696c5e",
      "futureStage": 3,
      "futureCourseVersionCode": "AT8-33"
    }
  ]
}
```

### 5. **Auto-Save Functionality**

- Automatically saves the generated JSON to the API configuration
- Updates session state
- Provides user feedback on successful processing

### 6. **Manual JSON Editing**

- Still allows manual JSON editing alongside Excel upload
- Shows JSON validation status
- Displays student count from processed data
- Auto-saves valid JSON changes

## UI Components

### Excel Upload Section

- File uploader with validation
- Data preview table
- Process button to convert and fill JSON
- Error handling for invalid files

### JSON Body Section (Enhanced)

- Expandable section for JSON editing
- Format JSON button with auto-save
- Validation feedback
- Student count display
- JSON structure preview

## File Structure

### Required Excel Columns

1. **StudentID** - Student UUID (converted to string)
2. **FutureStage** - Integer stage number
3. **FutureCourseVersionCode** - Course version code (string)

### Generated JSON Structure

- `students` array containing student objects
- Each student has `studentId`, `futureStage`, and `futureCourseVersionCode`

## Testing

A test script (`test_excel_upload.py`) is provided that:

- Creates a sample Excel file with test data
- Validates the JSON conversion logic
- Provides sample data for testing the feature

## Benefits

1. **User-Friendly**: Eliminates manual JSON entry for bulk student data
2. **Error Prevention**: Validates file format and required columns
3. **Flexible**: Supports both Excel upload and manual JSON editing
4. **Auto-Save**: Reduces risk of data loss
5. **Visual Feedback**: Shows data preview and processing status

## Integration

The feature integrates seamlessly with the existing API testing framework:

- Uses the same auto-save mechanism as other JSON editors
- Maintains compatibility with existing API configurations
- Preserves all existing functionality for non-AD APIs

This implementation significantly improves the user experience for AD module APIs that require bulk student data processing.
