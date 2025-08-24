# Mobile (Flutter) - Dynamic Question Renderer (Prototype)

This uses a single screen that fetches a Step from the backend and renders a widget based on `input.kind`.

## Create the project

```bash
# Requires Flutter SDK installed
flutter create ai_questionnaire
cd ai_questionnaire
```

## Add dependencies

In `pubspec.yaml` add under `dependencies:`:
```yaml
  http: ^1.2.2
```

Then run:
```bash
flutter pub get
```

## Replace `lib/main.dart`

Copy the provided `lib/main.dart` from this folder into your Flutter project.

## Run

```bash
# Ensure the backend is running on localhost:8000
flutter run -d ios    # or -d android
```
