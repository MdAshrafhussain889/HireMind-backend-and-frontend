"use client";

import { useEffect, useRef } from "react";
import { api } from "@/lib/api";

export function useProctoring(
  enabled: boolean,
  attemptId: string,
  token: string,
) {
  const warned = useRef(false);

  useEffect(() => {
    if (!enabled || !attemptId || !token) return;

    async function logEvent(eventType: string) {
      try {
        await api.logProctorEvent(token, {
          session_id: attemptId,
          event_type: eventType,
          timestamp: new Date().toISOString(),
        });
      } catch {
        // non-blocking
      }
    }

    function onVisibility() {
      if (document.hidden) {
        logEvent("tab_switch");
      }
    }

    function onFullscreen() {
      if (!document.fullscreenElement && warned.current) {
        logEvent("fullscreen_exit");
      }
    }

    function onCopy(e: ClipboardEvent) {
      e.preventDefault();
      logEvent("copy_paste");
    }

    document.addEventListener("visibilitychange", onVisibility);
    document.addEventListener("fullscreenchange", onFullscreen);
    document.addEventListener("copy", onCopy);

    // Request fullscreen once (user gesture may be required on some browsers)
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen?.().catch(() => {
        warned.current = true;
      });
    }

    return () => {
      document.removeEventListener("visibilitychange", onVisibility);
      document.removeEventListener("fullscreenchange", onFullscreen);
      document.removeEventListener("copy", onCopy);
    };
  }, [enabled, attemptId, token]);
}
