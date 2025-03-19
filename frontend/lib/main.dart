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
    return const MaterialApp(
      home: ChatPage(),
    );
  }
}

class ChatPage extends StatefulWidget {
  const ChatPage({super.key});

  @override
  _ChatPageState createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  bool isChatVisible = false;
  bool hasShownGreeting = false;

  List<ChatMessage> messages = [];
  final TextEditingController messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final FocusNode _messageFocusNode = FocusNode();

  void toggleChat() {
    setState(() {
      isChatVisible = !isChatVisible;

      if (isChatVisible && !hasShownGreeting) {
        messages.add(ChatMessage(text: "How can I help you?", isSent: false));
        hasShownGreeting = true;
      }
    });
  }

  void sendMessage() async {
    final messageText = messageController.text.trim();
    if (messageText.isEmpty) return;

    setState(() {
      messages.add(ChatMessage(text: messageText, isSent: true));
      messageController.clear();
    });

    // Add a placeholder message for streaming updates
    setState(() {
      messages.add(ChatMessage(text: '', isSent: false, isTyping: true));
    });

    scrollToBottom();

    try {
      final request = http.Request(
        'POST',
        Uri.parse("http://127.0.0.1:8080/ask"), // Streaming FastAPI endpoint
      );

      request.headers.addAll({"Content-Type": "application/json"});
      request.body = jsonEncode({"question": messageText});

      final streamedResponse = await http.Client().send(request);

      if (streamedResponse.statusCode == 200) {
        final responseStream = streamedResponse.stream.transform(utf8.decoder);

        String botResponse = "";
        String buffer = ""; // ✅ Store incomplete words
        int lastIndex = messages.length - 1; // ✅ Reference latest bot message

        await for (var chunk in responseStream) {
          String text = (buffer + chunk).trim(); // ✅ Trim unnecessary spaces
          List<String> words =
              text.split(RegExp(r'\s+')); // ✅ Split words properly

          if (words.length > 1) {
            buffer = words.removeLast(); // ✅ Keep last word if incomplete
          } else {
            buffer = ""; // ✅ Clear buffer if all words are complete
          }

          botResponse += " " + words.join(" "); // ✅ Append without replacing
          botResponse = botResponse
              .replaceAll(RegExp(r'\s+'), ' ')
              .trim(); // ✅ Normalize spaces

          setState(() {
            messages[lastIndex] = ChatMessage(text: botResponse, isSent: false);
          });

          scrollToBottom();
        }

        // ✅ Ensure final buffer is added
        if (buffer.isNotEmpty) {
          botResponse = (botResponse + " " + buffer).trim();
        }

        setState(() {
          messages[lastIndex] =
              ChatMessage(text: botResponse, isSent: false, isTyping: false);
        });
      } else {
        throw Exception("Failed to get response");
      }
    } catch (e) {
      setState(() {
        messages.removeWhere((msg) => msg.isTyping ?? false);
        messages.add(ChatMessage(
            text: "⚠️ Error: Unable to reach chatbot.", isSent: false));
      });
    }

    scrollToBottom();
  }

  void scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Mental Health Chatbot")),
      floatingActionButton: FloatingActionButton(
        onPressed: toggleChat,
        backgroundColor: Colors.green,
        child: Icon(isChatVisible ? Icons.close : Icons.chat),
      ),
      body: Stack(
        children: [
          buildWelcomeScreen(),
          if (isChatVisible) buildChatPopup(),
        ],
      ),
    );
  }

  Widget buildWelcomeScreen() {
    return const Center(
      child: Padding(
        padding: EdgeInsets.all(20.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              'Welcome to the Mental Health Chatbot tailored for UoE resources and support',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 20),
            Text(
              'Tap the chat icon to start a conversation.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 16),
            ),
          ],
        ),
      ),
    );
  }

  Widget buildChatPopup() {
    double screenHeight = MediaQuery.of(context).size.height;
    return Align(
      alignment: Alignment.bottomRight,
      child: Container(
        height: screenHeight * 0.6,
        width: 350,
        padding: const EdgeInsets.only(top: 8, right: 8, left: 8, bottom: 50),
        margin: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          boxShadow: [
            BoxShadow(blurRadius: 5, color: Colors.black.withOpacity(0.3))
          ],
          borderRadius: BorderRadius.circular(15),
        ),
        child: Column(
          children: [
            Expanded(
              child: ListView.builder(
                controller: _scrollController,
                itemCount: messages.length,
                itemBuilder: (context, index) {
                  final message = messages[index];
                  if (message.isTyping ?? false) {
                    return typingIndicator();
                  } else {
                    return messageWidget(message);
                  }
                },
              ),
            ),
            messageInputField(),
          ],
        ),
      ),
    );
  }

  Widget typingIndicator() {
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4, horizontal: 8),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const CircleAvatar(
              backgroundImage: AssetImage('assets/bear.png'),
              radius: 16,
            ),
            const SizedBox(width: 10),
            ...List.generate(
              3,
              (_) => Container(
                width: 8,
                height: 8,
                margin: const EdgeInsets.symmetric(horizontal: 2),
                decoration: const BoxDecoration(
                    color: Colors.grey, shape: BoxShape.circle),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget messageWidget(ChatMessage message) {
    bool isSentByUser = message.isSent;
    return Row(
      crossAxisAlignment:
          CrossAxisAlignment.end, // ✅ Aligns icon with text bubble
      mainAxisAlignment:
          isSentByUser ? MainAxisAlignment.end : MainAxisAlignment.start,
      children: [
        if (!isSentByUser) // ✅ Ensure avatar only appears for chatbot messages
          const Padding(
            padding: EdgeInsets.only(right: 8.0),
            child: Align(
              alignment:
                  Alignment.bottomLeft, // ✅ Keep the avatar at the bottom
              child: CircleAvatar(
                backgroundImage: AssetImage('assets/bear.png'),
                radius: 16,
              ),
            ),
          ),
        Flexible(
          child: Container(
            margin: const EdgeInsets.symmetric(vertical: 4, horizontal: 8),
            padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
            decoration: BoxDecoration(
              color: isSentByUser ? Colors.blue[100] : Colors.grey[200],
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              message.text,
              softWrap: true,
              overflow: TextOverflow.visible, // ✅ Ensures text wraps correctly
              textAlign: TextAlign.left, // ✅ Aligns text properly
            ),
          ),
        ),
      ],
    );
  }

  Widget messageInputField() {
    return Row(
      children: [
        Expanded(
          child: TextField(
            controller: messageController,
            focusNode: _messageFocusNode,
            decoration: const InputDecoration(
              hintText: "Type a message",
              border: OutlineInputBorder(
                  borderSide: BorderSide.none,
                  borderRadius: BorderRadius.all(Radius.circular(20))),
              filled: true,
              contentPadding: EdgeInsets.all(10),
            ),
            onSubmitted: (value) {
              sendMessage();
              Future.microtask(() => _messageFocusNode.requestFocus());
            },
          ),
        ),
        IconButton(
            icon: const Icon(Icons.send, color: Colors.blue),
            onPressed: sendMessage),
      ],
    );
  }
}

class ChatMessage {
  String text;
  bool isSent;
  bool? isTyping;

  ChatMessage(
      {required this.text, required this.isSent, this.isTyping = false});
}
