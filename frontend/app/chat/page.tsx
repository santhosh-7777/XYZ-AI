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
      const audio =
        new Audio(audioUrl);

      audioRef.current = audio;

      // Avatar starts speaking when
      // actual audio starts playing.
      audio.onplay = () => {
        setAvatarState("speaking");
      };

      // Audio finished.
      audio.onended = () => {
        audioRef.current = null;
        setAvatarState("idle");
        resolve();
      };

      // Browser could not load/play audio.
      audio.onerror = () => {
        audioRef.current = null;
        setAvatarState("error");

        reject(
          new Error(
            "Could not play assistant audio."
          )
        );
      };

      audio
        .play()
        .catch((error) => {
          audioRef.current = null;
          setAvatarState("error");
          reject(error);
        });
    });
  }

  // =========================================================
  // TEXT CHAT
  // =========================================================

  async function handleSend(
    e: React.FormEvent
  ) {
    e.preventDefault();

    if (!input.trim() || loading) return;

    const userMessage: Message = {
      role: "user",
      text: input,
    };

    setMessages((prev) => [
      ...prev,
      userMessage,
    ]);

    setInput("");
    setLoading(true);
    setAvatarState("thinking");

    try {
      const response =
        await api.post(
          "/ai/act",
          {
            text: userMessage.text,
          }
        );

      const result =
        response.data.result;

      const replyText =
        result?.message ||
        JSON.stringify(result) ||
        "No response.";

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: replyText,
        },
      ]);

      /*
       * Text chat currently uses the /ai/act endpoint.
       *
       * It does not return TTS audio yet.
       *
       * Therefore we only show the avatar response
       * state temporarily for text messages.
       *
       * Voice requests use real browser TTS below.
       */

      setAvatarState("speaking");

      window.setTimeout(() => {
        setAvatarState("idle");
      }, 2500);
    } catch (err: any) {
      // =====================================================
      // CONFIRMATION HANDLING
      // =====================================================

      if (
        err.response?.status === 409
      ) {
        const detail: string =
          err.response.data?.detail ||
          "";

        const match =
          detail.match(
            /action_id '([^']+)'/
          );

        if (match) {
          const actionId =
            match[1];

          try {
            const confirmResponse =
              await api.post(
                "/ai/confirm",
                {
                  action_id:
                    actionId,
                }
              );

            const confirmResult =
              confirmResponse.data.result;

            const replyText =
              confirmResult?.message ||
              JSON.stringify(
                confirmResult
              ) ||
              "Action confirmed.";

            setMessages((prev) => [
              ...prev,
              {
                role: "assistant",
                text: replyText,
              },
            ]);

            setAvatarState(
              "speaking"
            );

            window.setTimeout(() => {
              setAvatarState(
                "idle"
              );
            }, 2500);
          } catch {
            setAvatarState("error");

            setMessages((prev) => [
              ...prev,
              {
                role: "assistant",
                text:
                  "Error: could not confirm the pending action.",
              },
            ]);
          }
        } else {
          setAvatarState("error");

          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              text:
                "There's a pending action but I couldn't identify it.",
            },
          ]);
        }
      } else {
        setAvatarState("error");

        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            text:
              "Error: could not reach the assistant.",
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
      const stream =
        await navigator.mediaDevices.getUserMedia(
          {
            audio: true,
          }
        );

      const mediaRecorder =
        new MediaRecorder(stream);

      mediaRecorderRef.current =
        mediaRecorder;

      audioChunksRef.current = [];

      mediaRecorder.ondataavailable =
        (event) => {
          if (event.data.size > 0) {
            audioChunksRef.current.push(
              event.data
            );
          }
        };

      mediaRecorder.onstop =
        async () => {
          stream
            .getTracks()
            .forEach(
              (track) =>
                track.stop()
            );

          const audioBlob =
            new Blob(
              audioChunksRef.current,
              {
                type:
                  mediaRecorder.mimeType ||
                  "audio/webm",
              }
            );

          await sendVoice(
            audioBlob
          );
        };

      mediaRecorder.start();

      setRecording(true);
      setAvatarState("listening");
    } catch (error) {
      console.error(
        "Microphone error:",
        error
      );

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

    if (
      mediaRecorderRef.current
        .state !== "inactive"
    ) {
      mediaRecorderRef.current.stop();
    }

    setRecording(false);

    // Audio is now being processed.
    setAvatarState("thinking");
  }

  // =========================================================
  // SEND VOICE TO BACKEND
  // =========================================================

  async function sendVoice(
    audioBlob: Blob
  ) {
    setLoading(true);
    setAvatarState("thinking");

    try {
      const formData =
        new FormData();

      formData.append(
        "audio",
        audioBlob,
        "voice.webm"
      );

      const response =
        await api.post(
          "/voice/process",
          formData
        );

      const data =
        response.data;

      // =====================================================
      // SHOW WHAT WHISPER UNDERSTOOD
      // =====================================================

      if (data.text) {
        setMessages((prev) => [
          ...prev,
          {
            role: "user",
            text: data.text,
          },
        ]);
      }

      // =====================================================
      // EXTRACT AI RESPONSE
      // =====================================================

      const aiResult =
        data.ai_result;

      const result =
        aiResult?.result;

      const replyText =
        result?.message ||
        aiResult?.message ||
        JSON.stringify(
          result || aiResult
        ) ||
        "No response.";

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: replyText,
        },
      ]);

      // =====================================================
      // PLAY REAL TTS AUDIO
      // =====================================================

      if (data.audio_url) {
        /*
         * FastAPI returns:
         *
         * /voice/audio/<filename>.mp3
         *
         * Axios has the backend base URL.
         *
         * Example:
         *
         * http://127.0.0.1:8000
         *       +
         * /voice/audio/abc.mp3
         *
         * =
         *
         * http://127.0.0.1:8000/voice/audio/abc.mp3
         */

        const baseURL =
          api.defaults.baseURL ||
          "";

        const audioUrl =
          data.audio_url.startsWith(
            "http"
          )
            ? data.audio_url
            : `${baseURL}${data.audio_url}`;

        try {
          await playAssistantAudio(
            audioUrl
          );
        } catch (audioError) {
          console.error(
            "Audio playback failed:",
            audioError
          );

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
        /*
         * Backend did not return an audio URL.
         *
         * This usually means TTS generation failed
         * or the old backend is still running.
         */

        console.warn(
          "No audio_url returned from /voice/process."
        );

        setAvatarState("idle");
      }
    } catch (error: any) {
      console.error(
        "Voice request failed:",
        error
      );

      setAvatarState("error");

      let message =
        "Voice request failed. Please try again.";

      if (
        error.response?.data?.detail
      ) {
        message =
          `Voice error: ${error.response.data.detail}`;
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: message,
        },
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

  // =========================================================
  // UI
  // =========================================================

  return (
    <div className="flex h-screen flex-col bg-gray-50">

      {/* ===================================================
          HEADER
      =================================================== */}

      <header className="border-b bg-white px-6 py-4">
        <h1 className="text-xl font-bold">
          XYZ AI Assistant
        </h1>

        <p className="text-sm text-gray-500">
          Your human-like school assistant
        </p>
      </header>

      {/* ===================================================
          AVATAR
      =================================================== */}

      <div className="flex flex-col items-center justify-center bg-white px-6 py-6">

        <div
          className={`
            relative flex h-40 w-40 items-center
            justify-center rounded-full
            border-4 bg-gray-100
            transition-all duration-300

            ${
              avatarState === "listening"
                ? "scale-105 border-blue-500 shadow-lg shadow-blue-200"
                : ""
            }

            ${
              avatarState === "thinking"
                ? "animate-pulse border-yellow-500"
                : ""
            }

            ${
              avatarState === "speaking"
                ? "scale-105 border-green-500 shadow-lg shadow-green-200"
                : ""
            }

            ${
              avatarState === "error"
                ? "border-red-500"
                : ""
            }

            ${
              avatarState === "idle"
                ? "border-gray-300"
                : ""
            }
          `}
        >

          {/* =================================================
              AVATAR FACE
          ================================================= */}

          <div className="relative flex h-28 w-28 items-center justify-center rounded-full bg-gray-200">

            {/* Hair */}

            <div className="absolute -top-2 h-10 w-24 rounded-t-full bg-gray-800" />

            {/* Face */}

            <div className="relative mt-3 h-20 w-20 rounded-full bg-gray-100">

              {/* Left eye */}

              <div className="absolute left-5 top-8 h-2 w-2 rounded-full bg-black" />

              {/* Right eye */}

              <div className="absolute right-5 top-8 h-2 w-2 rounded-full bg-black" />

              {/* Mouth */}

              <div
                className={`
                  absolute left-1/2 top-12
                  -translate-x-1/2
                  rounded-full bg-black
                  transition-all duration-150

                  ${
                    avatarState ===
                    "speaking"
                      ? "h-4 w-6"
                      : "h-1 w-6"
                  }
                `}
              />

            </div>
          </div>

          {/* =================================================
              SPEAKING INDICATOR
          ================================================= */}

          {avatarState ===
            "speaking" && (
            <div className="absolute -bottom-2 flex gap-1">

              <span className="h-2 w-2 animate-bounce rounded-full bg-green-500" />

              <span className="h-2 w-2 animate-bounce rounded-full bg-green-500 [animation-delay:150ms]" />

              <span className="h-2 w-2 animate-bounce rounded-full bg-green-500 [animation-delay:300ms]" />

            </div>
          )}

          {/* =================================================
              LISTENING INDICATOR
          ================================================= */}

          {avatarState ===
            "listening" && (
            <div className="absolute -bottom-2 h-4 w-4 animate-ping rounded-full bg-blue-500" />
          )}

        </div>

        <h2 className="mt-4 text-lg font-semibold">
          XYZ AI
        </h2>

        <p className="text-sm text-gray-500">
          {avatarLabel}
        </p>

      </div>

      {/* ===================================================
          MESSAGES
      =================================================== */}

      <div className="flex-1 space-y-4 overflow-y-auto px-6 py-4">

        {messages.map(
          (msg, i) => (
            <div
              key={i}
              className={`flex ${
                msg.role === "user"
                  ? "justify-end"
                  : "justify-start"
              }`}
            >

              <div
                className={`
                  max-w-md rounded-lg px-4 py-2

                  ${
                    msg.role ===
                    "user"
                      ? "bg-black text-white"
                      : "border bg-white text-gray-800"
                  }
                `}
              >
                {msg.text}
              </div>

            </div>
          )
        )}

        {/* =================================================
            PROCESSING INDICATOR
        ================================================= */}

        {loading && (
          <div className="flex justify-start">

            <div className="rounded-lg border bg-white px-4 py-2 text-gray-400">

              {recording
                ? "Listening..."
                : "Thinking..."}

            </div>

          </div>
        )}

        <div ref={bottomRef} />

      </div>

      {/* ===================================================
          COMPOSER
      =================================================== */}

      <form
        onSubmit={handleSend}
        className="border-t bg-white px-6 py-4"
      >

        <div className="flex gap-2">

          {/* TEXT INPUT */}

          <input
            type="text"
            value={input}
            onChange={(e) =>
              setInput(
                e.target.value
              )
            }
            placeholder="Ask me anything..."
            disabled={
              loading ||
              recording
            }
            className="
              flex-1 rounded-lg
              border px-4 py-3
              outline-none
              focus:border-black
            "
          />

          {/* MICROPHONE */}

          <button
            type="button"
            onClick={
              recording
                ? stopRecording
                : startRecording
            }
            disabled={loading}
            className={`
              rounded-lg px-4 py-3
              text-white transition

              ${
                recording
                  ? "bg-red-600"
                  : "bg-blue-600"
              }

              disabled:opacity-50
            `}
          >
            {recording
              ? "⏹"
              : "🎤"}
          </button>

          {/* SEND */}

          <button
            type="submit"
            disabled={
              loading ||
              recording ||
              !input.trim()
            }
            className="
              rounded-lg
              bg-black
              px-5 py-3
              text-white
              disabled:opacity-50
            "
          >
            Send
          </button>

        </div>

      </form>

    </div>
  );
}