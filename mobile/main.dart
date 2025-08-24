\
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI Questionnaire',
      home: const SessionScreen(),
    );
  }
}

class StepModel {
  final String id;
  final String type;
  final Map<String, dynamic>? question;
  final Map<String, dynamic> ui;
  final Map<String, dynamic> context;

  StepModel({required this.id, required this.type, required this.question, required this.ui, required this.context});

  factory StepModel.fromJson(Map<String, dynamic> json) => StepModel(
    id: json['id'],
    type: json['type'],
    question: json['question'],
    ui: (json['ui'] ?? {}) as Map<String, dynamic>,
    context: (json['context'] ?? {}) as Map<String, dynamic>,
  );
}

class SessionScreen extends StatefulWidget {
  const SessionScreen({super.key});
  @override
  State<SessionScreen> createState() => _SessionScreenState();
}

class _SessionScreenState extends State<SessionScreen> {
  String? sessionId;
  StepModel? currentStep;
  dynamic currentAnswer;
  bool loading = false;
  final backend = const String.fromEnvironment('BACKEND_URL', defaultValue: 'http://localhost:8000');

  @override
  void initState() {
    super.initState();
    _startSession();
  }

  Future<void> _startSession() async {
    setState(() { loading = true; });
    final res = await http.post(Uri.parse('$backend/sessions'), headers: {'Content-Type': 'application/json'}, body: '{}');
    final data = jsonDecode(res.body) as Map<String, dynamic>;
    setState(() {
      sessionId = data['session_id'] as String;
      currentStep = StepModel.fromJson(data['step'] as Map<String, dynamic>);
      currentAnswer = null;
      loading = false;
    });
  }

  Future<void> _sendAnswer(String questionId, dynamic answerPayload) async {
    if (sessionId == null) return;
    setState(() { loading = true; });
    final body = jsonEncode({
      'session_id': sessionId,
      'question_id': questionId,
      'answer': answerPayload,
    });
    final res = await http.post(Uri.parse('$backend/sessions/$sessionId/answer'),
        headers: {'Content-Type': 'application/json'}, body: body);
    final data = jsonDecode(res.body) as Map<String, dynamic>;
    setState(() {
      currentStep = StepModel.fromJson(data['step'] as Map<String, dynamic>);
      currentAnswer = null;
      loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final step = currentStep;
    return Scaffold(
      appBar: AppBar(title: const Text('AI Questionnaire')),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : step == null
              ? Center(
                  child: ElevatedButton(
                    onPressed: _startSession,
                    child: const Text('Start'),
                  ),
                )
              : Padding(
                  padding: const EdgeInsets.all(16),
                  child: _buildStep(step),
                ),
    );
  }

  Widget _buildStep(StepModel step) {
    if (step.type == 'info') {
      final summary = step.context['summary']?.toString() ?? 'Done!';
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Summary', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          Text(summary),
          const Spacer(),
          ElevatedButton(onPressed: _startSession, child: const Text('Restart')),
        ],
      );
    }

    // Additional safety check for question
    if (step.question == null) {
      return const Center(
        child: Text('Error: Missing question data'),
      );
    }

    final q = step.question!;
    final label = q['label'] as String;
    final input = q['input'] as Map<String, dynamic>;
    final kind = input['kind'] as String;
    final help = q['help']?.toString();

    Widget inputWidget;

    switch (kind) {
      case 'free_text':
        inputWidget = TextField(
          decoration: InputDecoration(labelText: label, helperText: help, hintText: input['placeholder']?.toString()),
          onChanged: (v) => currentAnswer = {'kind': 'free_text', 'value': v},
        );
        break;
      case 'yes_no':
        inputWidget = Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label, style: const TextStyle(fontSize: 16)),
            Row(children: [
              Expanded(child: RadioListTile<bool>(
                title: const Text('Yes'),
                value: true,
                groupValue: currentAnswer?['value'] as bool?,
                onChanged: (v) => setState(() => currentAnswer = {'kind': 'yes_no', 'value': v}),
              )),
              Expanded(child: RadioListTile<bool>(
                title: const Text('No'),
                value: false,
                groupValue: currentAnswer?['value'] as bool?,
                onChanged: (v) => setState(() => currentAnswer = {'kind': 'yes_no', 'value': v}),
              )),
            ]),
          ],
        );
        break;
      case 'multiple_choice':
        final options = (input['options'] as List).cast<Map>();
        final selected = currentAnswer?['value'] as String?;
        inputWidget = Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label, style: const TextStyle(fontSize: 16)),
            const SizedBox(height: 8),
            ...options.map((opt) => RadioListTile<String>(
              title: Text(opt['label'] as String),
              value: opt['value'] as String,
              groupValue: selected,
              onChanged: (v) => setState(() => currentAnswer = {'kind': 'multiple_choice', 'value': v}),
            )),
          ],
        );
        break;
      case 'multi_select':
        final options = (input['options'] as List).cast<Map>();
        final Set<String> selected = Set.from((currentAnswer?['value'] as List?) ?? []);
        inputWidget = Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label, style: const TextStyle(fontSize: 16)),
            const SizedBox(height: 8),
            ...options.map((opt) {
              final val = opt['value'] as String;
              final isChecked = selected.contains(val);
              return CheckboxListTile(
                title: Text(opt['label'] as String),
                value: isChecked,
                onChanged: (v) {
                  setState(() {
                    if (v == true) {
                      selected.add(val);
                    } else {
                      selected.remove(val);
                    }
                    currentAnswer = {'kind': 'multi_select', 'value': selected.toList()};
                  });
                },
              );
            }),
          ],
        );
        break;
      default:
        inputWidget = Text('Unsupported input type: $kind');
    }

    final qid = q['id'] as String;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        inputWidget,
        const Spacer(),
        ElevatedButton(
          onPressed: currentAnswer == null ? null : () => _sendAnswer(qid, currentAnswer),
          child: Text(step.ui['next_button_label']?.toString() ?? 'Continue'),
        ),
      ],
    );
  }
}
