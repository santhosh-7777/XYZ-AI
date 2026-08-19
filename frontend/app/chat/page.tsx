"use client";

import { useState, useRef, useEffect } from "react";
import api from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  text: string;
}

type AvatarState =
  | "idle"
  | "listening"
  | "thinking"
  | "speaking"
  | "error";

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [recording, setRecording] = useState(false);

  const [avatarState, setAvatarState] =
    useState<AvatarState>("idle");

  const bottomRef = useRef<HTMLDivElement>(null);

  const mediaRecorderRef =
    useRef<MediaRecorder | null>(null);

  const audioChunksRef =
    useRef<Blob[]>([]);

  const audioRef =
    useRef<HTMLAudioElement | null>(null);

  // =========================================================
  // AUTO SCROLL
  // =========================================================

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages]);

  // =========================================================
  // CLEANUP AUDIO WHEN PAGE UNMOUNTS
  // =========================================================

  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.src = "";
        audioRef.current = null;
      }
    };
  }, []);

  // =========================================================
  // PLAY ASSISTANT TTS AUDIO
  // =========================================================

  async function playAssistantAudio(
    audioUrl: string
  ): Promise<void> {
    return new Promise((resolve, reject) => {
      const audio = new Audio(audioUrl);

      audioRef.current = audio;

      audio.onplay = () => {
        setAvatarState("speaking");
      };

      audio.onended = () => {
        audioRef.current = null;
        setAvatarState("idle");
        resolve();
      };

      audio.onerror = () => {
        audioRef.current = null;
        setAvatarState("error");

        reject(
          new Error("Could not play assistant audio.")
        );
      };

      audio.play().catch((error) => {
        audioRef.current = null;
        setAvatarState("error");
        reject(error);
      });
    });
  }

  // =========================================================
  // TEXT CHAT
  // =========================================================

  async function handleSend(e: React.FormEvent) {
    e.preventDefault();

    if (!input.trim() || loading) return;

    const userMessage: Message = {
      role: "user",
      text: input,
    };

    setMessages((prev) => [...prev, userMessage]);

    setInput("");
    setLoading(true);
    setAvatarState("thinking");

    try {
      const response = await api.post("/ai/act", {
        text: userMessage.text,
      });

      const result = response.data.result;

      const replyText =
        result?.message ||
        JSON.stringify(result) ||
        "No response.";

      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: replyText },
      ]);

      setAvatarState("speaking");

      window.setTimeout(() => {
        setAvatarState("idle");
      }, 2500);
    } catch (err: any) {
      if (err.response?.status === 409) {
        const detail: string = err.response.data?.detail || "";

        const match = detail.match(/action_id '([^']+)'/);

        if (match) {
          const actionId = match[1];

          try {
            const confirmResponse = await api.post("/ai/confirm", {
              action_id: actionId,
            });

            const confirmResult = confirmResponse.data.result;

            const replyText =
              confirmResult?.message ||
              JSON.stringify(confirmResult) ||
              "Action confirmed.";

            setMessages((prev) => [
              ...prev,
              { role: "assistant", text: replyText },
            ]);

            setAvatarState("speaking");

            window.setTimeout(() => {
              setAvatarState("idle");
            }, 2500);
          } catch {
            setAvatarState("error");

            setMessages((prev) => [
              ...prev,
              {
                role: "assistant",
                text: "Error: could not confirm the pending action.",
              },
            ]);
          }
        } else {
          setAvatarState("error");

          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              text: "There's a pending action but I couldn't identify it.",
            },
          ]);
        }
      } else {
        setAvatarState("error");

        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            text: "Error: could not reach the assistant.",
          },
        ]);
      }
    } finally {
      setLoading(false);
    }
  }

  // =========================================================
  // VOICE CHAT
  // =========================================================

  async function startRecording() {
    if (loading || recording) return;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });

      const mediaRecorder = new MediaRecorder(stream);

      mediaRecorderRef.current = mediaRecorder;

      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach((track) => track.stop());

        const audioBlob = new Blob(audioChunksRef.current, {
          type: mediaRecorder.mimeType || "audio/webm",
        });

        await sendVoice(audioBlob);
      };

      mediaRecorder.start();

      setRecording(true);
      setAvatarState("listening");
    } catch (error) {
      console.error("Microphone error:", error);

      setAvatarState("error");

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text:
            "Could not access the microphone. Please allow microphone permission and try again.",
        },
      ]);
    }
  }

  // =========================================================
  // STOP RECORDING
  // =========================================================

  function stopRecording() {
    if (!mediaRecorderRef.current) {
      return;
    }

    if (mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
    }

    setRecording(false);
    setAvatarState("thinking");
  }

  // =========================================================
  // SEND VOICE TO BACKEND
  // =========================================================

  async function sendVoice(audioBlob: Blob) {
    setLoading(true);
    setAvatarState("thinking");

    try {
      const formData = new FormData();

      formData.append("audio", audioBlob, "voice.webm");

      const response = await api.post("/voice/process", formData);

      const data = response.data;

      if (data.text) {
        setMessages((prev) => [
          ...prev,
          { role: "user", text: data.text },
        ]);
      }

      const aiResult = data.ai_result;

      const result = aiResult?.result;

      const replyText =
        result?.message ||
        aiResult?.message ||
        JSON.stringify(result || aiResult) ||
        "No response.";

      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: replyText },
      ]);

      if (data.audio_url) {
        const baseURL = api.defaults.baseURL || "";

        const audioUrl = data.audio_url.startsWith("http")
          ? data.audio_url
          : `${baseURL}${data.audio_url}`;

        try {
          await playAssistantAudio(audioUrl);
        } catch (audioError) {
          console.error("Audio playback failed:", audioError);

          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              text:
                "I generated the response, but I could not play the voice audio.",
            },
          ]);

          setAvatarState("error");
        }
      } else {
        console.warn("No audio_url returned from /voice/process.");

        setAvatarState("idle");
      }
    } catch (error: any) {
      console.error("Voice request failed:", error);

      setAvatarState("error");

      let message = "Voice request failed. Please try again.";

      if (error.response?.data?.detail) {
        message = `Voice error: ${error.response.data.detail}`;
      }

      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: message },
      ]);
    } finally {
      setLoading(false);
    }
  }

  // =========================================================
  // AVATAR STATE
  // =========================================================

  const avatarLabel = {
    idle: "Ready to help",
    listening: "Listening...",
    thinking: "Thinking...",
    speaking: "Speaking...",
    error: "Something went wrong",
  }[avatarState];

  // Orb gradient + glow per state — this is the avatar
  const orbGradient = {
    idle: "from-zinc-300 via-zinc-200 to-zinc-100",
    listening: "from-sky-400 via-blue-400 to-cyan-300",
    thinking: "from-amber-400 via-orange-300 to-yellow-200",
    speaking: "from-emerald-400 via-teal-400 to-green-300",
    error: "from-red-400 via-rose-400 to-red-300",
  }[avatarState];

  const orbGlow = {
    idle: "shadow-[0_0_50px_-10px_rgba(0,0,0,0.15)]",
    listening: "shadow-[0_0_90px_-10px_rgba(56,189,248,0.55)]",
    thinking: "shadow-[0_0_90px_-10px_rgba(251,191,36,0.55)]",
    speaking: "shadow-[0_0_90px_-10px_rgba(52,211,153,0.55)]",
    error: "shadow-[0_0_90px_-10px_rgba(248,113,113,0.55)]",
  }[avatarState];

  // =========================================================
  // UI
  // =========================================================

  return (
    <div className="flex h-screen flex-col bg-white text-zinc-900 sm:flex-row">

      {/* ===================================================
          LEFT — persistent chat thread
      =================================================== */}

      <div className="flex h-1/2 w-full flex-col border-zinc-100 sm:h-full sm:w-[400px] sm:border-r md:w-[440px]">

        <header className="shrink-0 border-b border-zinc-100 px-5 py-4">
          <h1 className="text-sm font-semibold tracking-wide">
            XYZ AI
          </h1>
          <p className="text-xs text-zinc-400">
            School Assistant
          </p>
        </header>

        {/* MESSAGE THREAD */}

        <div className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
          {messages.length === 0 && (
            <p className="mt-4 text-center text-xs text-zinc-400">
              Say hello, or ask about attendance.
            </p>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${
                msg.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`
                  max-w-[80%] rounded-2xl px-3.5 py-2 text-sm leading-relaxed
                  ${
                    msg.role === "user"
                      ? "rounded-br-sm bg-zinc-900 text-white"
                      : "rounded-bl-sm border border-zinc-100 bg-zinc-50 text-zinc-800"
                  }
                `}
              >
                {msg.text}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="rounded-2xl rounded-bl-sm border border-zinc-100 bg-zinc-50 px-3.5 py-2 text-sm text-zinc-400">
                {recording ? "Listening..." : "Thinking..."}
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* COMPOSER — bottom of chat panel */}

        <form
          onSubmit={handleSend}
          className="shrink-0 border-t border-zinc-100 px-4 py-3"
        >
          <div className="flex items-center gap-2">

            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask XYZ AI..."
              disabled={loading || recording}
              className="
                flex-1 rounded-full border border-zinc-200
                bg-zinc-50 px-4 py-2 text-sm text-zinc-900
                outline-none placeholder:text-zinc-400
                focus:border-zinc-400
              "
            />

            <button
              type="button"
              onClick={recording ? stopRecording : startRecording}
              disabled={loading}
              className={`
                flex h-9 w-9 shrink-0 items-center justify-center
                rounded-full text-sm text-white transition
                ${recording ? "bg-red-500" : "bg-zinc-900 hover:bg-zinc-700"}
                disabled:opacity-50
              `}
            >
              {recording ? "⏹" : "🎤"}
            </button>

            <button
              type="submit"
              disabled={loading || recording || !input.trim()}
              className="
                h-9 shrink-0 rounded-full bg-zinc-900 px-4
                text-sm font-medium text-white
                disabled:opacity-40
              "
            >
              Send
            </button>
          </div>
        </form>
      </div>

      {/* ===================================================
          RIGHT — large orb avatar
      =================================================== */}

      <div className="relative flex h-1/2 flex-1 flex-col items-center justify-center overflow-hidden sm:h-full">

        <div
          className={`
            relative h-56 w-56 rounded-full bg-gradient-to-br
            transition-all duration-500 ease-out sm:h-80 sm:w-80
            ${orbGradient} ${orbGlow}
            ${avatarState === "listening" ? "scale-105" : "scale-100"}
            ${avatarState === "thinking" ? "animate-pulse" : ""}
          `}
        >
          {/* inner highlight for depth */}
          <div className="absolute left-[18%] top-[14%] h-[30%] w-[30%] rounded-full bg-white/50 blur-xl" />

          {/* soft moving core, breathes when speaking */}
          <div
            className={`
              absolute inset-6 rounded-full bg-white/25 backdrop-blur-sm
              transition-transform duration-700
              ${
                avatarState === "speaking"
                  ? "animate-[pulse_1s_ease-in-out_infinite] scale-100"
                  : "scale-90"
              }
            `}
          />

          {/* listening ring pulse */}
          {avatarState === "listening" && (
            <span className="absolute inset-0 animate-ping rounded-full bg-sky-300/40" />
          )}
        </div>

        <p className="mt-8 text-sm font-medium text-zinc-500">
          {avatarLabel}
        </p>
      </div>
    </div>
  );
}