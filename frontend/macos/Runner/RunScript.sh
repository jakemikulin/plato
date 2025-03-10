#!/bin/bash
echo "📂 Copying backend and virtual environment to macOS app bundle..."
cp -r ../../backend "$TARGET_BUILD_DIR/$CONTENTS_FOLDER_PATH/Resources/"
cp -r ../../backend/.venv "$TARGET_BUILD_DIR/$CONTENTS_FOLDER_PATH/Resources/backend/"
echo "✅ Backend and virtual environment copied successfully!"
