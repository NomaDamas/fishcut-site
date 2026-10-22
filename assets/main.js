// fishcut landing. Progressive enhancement only:
// every text and image is in the HTML, this file adds motion and controls on top.
(() => {
  "use strict";

  // Text this script writes into the page. The page's lang attribute picks the set.
  const TEXT = {
    ko: {
      play: "재생",
      pause: "멈춤",
      phonePlay: "완성 쇼츠 재생",
      phonePause: "완성 쇼츠 멈춤",
      editPlay: "편집 녹화 재생",
      editPause: "편집 녹화 멈춤",
      autoPlay: "자동 넘김 재생",
      autoPause: "자동 넘김 멈춤",
      step: (n, total, title) => `${total}단계 중 ${n}단계: ${title}`,
      copied: "복사했습니다",
      copyFailed: "직접 선택해 복사하세요",
      ytPlayer: (title) => `YouTube 플레이어: ${title}`,
      videoPlayer: (title) => `영상: ${title}`,
    },
    en: {
      play: "Play",
      pause: "Pause",
      phonePlay: "Play the finished short",
      phonePause: "Pause the finished short",
      editPlay: "Play the editing recording",
      editPause: "Pause the editing recording",
      autoPlay: "Resume auto-advance",
      autoPause: "Pause auto-advance",
      step: (n, total, title) => `Step ${n} of ${total}: ${title}`,
      copied: "Copied",
      copyFailed: "Select the text and copy it",
      ytPlayer: (title) => `YouTube player: ${title}`,
      videoPlayer: (title) => `Video: ${title}`,
    },
  };
  const t = TEXT[document.documentElement.lang] || TEXT.ko;

  const reduceMQ = window.matchMedia("(prefers-reduced-motion: reduce)");
  const hoverMQ = window.matchMedia("(hover: hover) and (pointer: fine)");
  const reduced = () => reduceMQ.matches;
  const onMQChange = (mq, fn) => {
    if (mq.addEventListener) mq.addEventListener("change", fn);
    else if (mq.addListener) mq.addListener(fn);
  };

  // Muted play that never throws. Browsers without H.264 keep the poster.
  const play = (video) => {
    if (!video || video.dataset.failed) return;
    video.muted = true;
    const result = video.play();
    if (result && result.catch) {
      result.catch((err) => {
        if (err && err.name === "NotSupportedError") video.dataset.failed = "1";
      });
    }
  };

  // Hero wall: play only the tiles that are on screen, pause everything when
  // the hero leaves the viewport, the tab hides, or motion is turned off.
  function initWall() {
    const stage = document.querySelector("[data-wall]");
    if (!stage) return;
    const hero = stage.closest(".hero") || stage;
    const toggle = stage.querySelector(".motion-input");
    const videos = Array.from(stage.querySelectorAll(".tile video"));
    let onScreen = true;
    let timer = 0;

    const canMove = () => !reduced() && !(toggle && toggle.checked) && !document.hidden;
    const check = () => {
      const vw = window.innerWidth;
      const vh = window.innerHeight;
      for (const video of videos) {
        const r = video.getBoundingClientRect();
        const visible = r.right > 0 && r.left < vw && r.bottom > 0 && r.top < vh;
        if (onScreen && canMove() && visible) play(video);
        else if (!video.paused) video.pause();
      }
    };
    const schedule = () => {
      window.clearInterval(timer);
      timer = 0;
      check();
      if (onScreen && canMove()) timer = window.setInterval(check, 900);
    };

    if ("IntersectionObserver" in window) {
      new IntersectionObserver((entries) => {
        onScreen = entries[entries.length - 1].isIntersecting;
        hero.classList.toggle("is-offscreen", !onScreen);
        schedule();
      }).observe(stage);
    } else {
      schedule();
    }
    if (toggle) toggle.addEventListener("change", schedule);
    document.addEventListener("visibilitychange", schedule);
    onMQChange(reduceMQ, schedule);
  }

  // Composer: type the example sentence once. Screen readers get the full
  // sentence from a hidden copy; the ghost copy keeps the box from resizing.
  function initTyping() {
    const el = document.querySelector("[data-typing]");
    if (!el || reduced()) return;
    const nodes = [];
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) nodes.push(walker.currentNode);
    const full = nodes.map((n) => n.nodeValue);
    nodes.forEach((n) => {
      n.nodeValue = "";
    });
    let ni = 0;
    let ci = 0;
    const step = () => {
      while (ni < nodes.length && ci >= full[ni].length) {
        ni += 1;
        ci = 0;
      }
      if (ni >= nodes.length) return;
      ci += 1;
      nodes[ni].nodeValue = full[ni].slice(0, ci);
      const ch = full[ni][ci - 1];
      window.setTimeout(step, ch === " " ? 55 : ch === "." ? 220 : 26 + Math.random() * 30);
    };
    window.setTimeout(step, 450);
  }

  // Editing recording in the demo window: plays muted while the window is on
  // screen, unless motion is reduced or the visitor paused it. The step list
  // under it marks the step on screen once the recording has started.
  function initEditDemo() {
    const win = document.querySelector("[data-edit-demo]");
    if (!win) return;
    const video = win.querySelector("video");
    const btn = win.querySelector("[data-edit-play]");
    if (!video || !btn) return;
    const label = btn.querySelector("span");
    const list = document.querySelector("[data-edit-steps]");
    const steps = list ? Array.from(list.children) : [];
    let userPaused = reduced();
    let onScreen = false;

    const render = () => {
      const on = !video.paused;
      win.classList.toggle("is-playing", on);
      label.textContent = on ? t.pause : t.play;
      btn.setAttribute("aria-label", on ? t.editPause : t.editPlay);
    };
    const sync = () => {
      if (onScreen && !userPaused && !document.hidden) play(video);
      else if (!video.paused) video.pause();
    };
    const mark = () => {
      let current = -1;
      steps.forEach((li, i) => {
        if (video.currentTime >= Number(li.dataset.t)) current = i;
      });
      steps.forEach((li, i) => {
        li.classList.toggle("is-current", i === current);
        if (i === current) li.setAttribute("aria-current", "step");
        else li.removeAttribute("aria-current");
      });
    };

    btn.hidden = false;
    btn.addEventListener("click", () => {
      userPaused = !video.paused;
      if (userPaused) video.pause();
      else play(video);
    });
    video.addEventListener("playing", () => {
      win.classList.add("is-started");
      if (list) list.classList.add("is-live");
      render();
    });
    video.addEventListener("pause", render);
    video.addEventListener("timeupdate", mark);

    if ("IntersectionObserver" in window) {
      new IntersectionObserver(
        (entries) => {
          onScreen = entries[entries.length - 1].isIntersecting;
          sync();
        },
        { threshold: 0.4 },
      ).observe(win);
    }
    document.addEventListener("visibilitychange", sync);
    onMQChange(reduceMQ, () => {
      if (reduced()) userPaused = true;
      sync();
    });
  }

  // Phone in the demo: plays only when the visitor presses the button.
  function initPhone() {
    const fig = document.querySelector("[data-phone]");
    if (!fig) return;
    const video = fig.querySelector(".phone video");
    const btn = fig.querySelector("[data-phone-play]");
    if (!video || !btn) return;
    const label = btn.querySelector("span");
    btn.hidden = false;
    const render = () => {
      const on = !video.paused;
      fig.classList.toggle("is-playing", on);
      label.textContent = on ? t.pause : t.play;
      btn.setAttribute("aria-label", on ? t.phonePause : t.phonePlay);
    };
    btn.addEventListener("click", () => {
      if (video.paused) play(video);
      else video.pause();
    });
    video.addEventListener("playing", render);
    video.addEventListener("pause", render);
  }

  // Real shorts: hover or keyboard focus previews the silent loop. "Play here"
  // puts the player in place of the poster, one card at a time. A YouTube card
  // loads the privacy-enhanced player only after the click, so the page sends
  // nothing to YouTube before it. Nothing is drawn over a player.
  function initShorts() {
    const cards = Array.from(document.querySelectorAll("[data-short]"));
    const close = (card) => {
      const player = card.querySelector("[data-player]");
      if (!player) return;
      player.remove();
      card.classList.remove("is-embed");
      card.querySelector("[data-short-play]").hidden = false;
    };
    for (const card of cards) {
      const media = card.querySelector(".short-media");
      const loop = media.querySelector("video");
      const btn = card.querySelector("[data-short-play]");
      const title = card.querySelector(".short-title").textContent;
      const start = () => {
        if (!reduced() && !card.classList.contains("is-embed")) play(loop);
      };
      const stop = () => {
        loop.pause();
        card.classList.remove("is-playing");
      };
      loop.addEventListener("playing", () => card.classList.add("is-playing"));
      if (hoverMQ.matches) {
        card.addEventListener("mouseenter", start);
        card.addEventListener("mouseleave", stop);
      }
      card.addEventListener("focusin", start);
      card.addEventListener("focusout", stop);

      btn.hidden = false;
      btn.addEventListener("click", () => {
        for (const other of cards) if (other !== card) close(other);
        stop();
        let player;
        if (card.dataset.yt) {
          player = document.createElement("iframe");
          player.src = `https://www.youtube-nocookie.com/embed/${encodeURIComponent(card.dataset.yt)}?autoplay=1&playsinline=1&rel=0`;
          player.title = t.ytPlayer(title);
          player.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
          player.allowFullscreen = true;
          player.referrerPolicy = "strict-origin-when-cross-origin";
        } else {
          player = document.createElement("video");
          player.src = card.dataset.src;
          player.controls = true;
          player.playsInline = true;
          player.setAttribute("aria-label", t.videoPlayer(title));
          const result = player.play();
          if (result && result.catch) result.catch(() => {});
        }
        player.className = "short-player";
        player.dataset.player = "";
        media.append(player);
        card.classList.add("is-embed");
        btn.hidden = true;
        player.focus();
      });
    }
  }

  // Story reel for the 8 steps. Without JS it stays a scroll-snap list.
  function initReel() {
    const root = document.querySelector("[data-reel]");
    if (!root) return;
    const track = root.querySelector(".reel-track");
    const slides = Array.from(track.children);
    const segs = Array.from(root.querySelectorAll(".seg"));
    const prevBtn = root.querySelector("[data-reel-prev]");
    const nextBtn = root.querySelector("[data-reel-next]");
    const playBtn = root.querySelector("[data-reel-play]");
    const playLabel = root.querySelector("[data-reel-play-label]");
    const count = root.querySelector("[data-reel-count]");
    const status = root.querySelector("[data-reel-status]");
    const total = slides.length;

    let index = 0;
    let userPaused = reduced();
    let hoverPaused = false;
    let focusPaused = false;
    let offscreen = true;
    let programmatic = false;
    let settleTimer = 0;
    let unlockTimer = 0;

    root.classList.add("is-enhanced");
    root.querySelectorAll("[data-reel-ui]").forEach((el) => {
      el.hidden = false;
    });

    const paused = () => userPaused || hoverPaused || focusPaused || offscreen;
    const title = (i) => slides[i].querySelector("h3").textContent.trim();

    const renderState = () => {
      root.classList.toggle("is-paused", paused());
      root.classList.toggle("is-user-paused", userPaused);
      playLabel.textContent = userPaused ? t.autoPlay : t.autoPause;
    };

    const render = () => {
      slides.forEach((s, i) => s.classList.toggle("is-active", i === index));
      segs.forEach((g, i) => {
        g.classList.toggle("is-done", i < index);
        g.classList.toggle("is-current", i === index);
        if (i === index) g.setAttribute("aria-current", "step");
        else g.removeAttribute("aria-current");
      });
      count.textContent = `${index + 1} / ${total}`;
      renderState();
    };

    const restartFill = () => {
      segs.forEach((g) => g.classList.remove("is-running"));
      if (reduced() || userPaused) return;
      const seg = segs[index];
      void seg.offsetWidth; // restart the CSS animation
      seg.classList.add("is-running");
    };

    // cards snap to the start edge of the track (after its scroll padding)
    const padStart = () => parseFloat(getComputedStyle(track).scrollPaddingLeft) || 0;
    const startOf = (i) => slides[i].offsetLeft - padStart();

    const scrollTo = (i, smooth) => {
      const left = Math.max(0, Math.min(startOf(i), track.scrollWidth - track.clientWidth));
      if (Math.abs(track.scrollLeft - left) < 2) return;
      programmatic = true;
      window.clearTimeout(unlockTimer);
      unlockTimer = window.setTimeout(() => {
        programmatic = false;
      }, 900);
      track.scrollTo({ left, behavior: smooth && !reduced() ? "smooth" : "auto" });
    };

    const go = (i, opts = {}) => {
      index = (i + total) % total;
      scrollTo(index, opts.smooth !== false);
      render();
      restartFill();
      if (opts.announce && status) status.textContent = t.step(index + 1, total, title(index));
    };

    // auto advance when the running fill finishes
    root.addEventListener("animationend", (e) => {
      if (e.animationName === "seg-fill" && !paused()) go(index + 1);
    });

    prevBtn.addEventListener("click", () => go(index - 1, { announce: true }));
    nextBtn.addEventListener("click", () => go(index + 1, { announce: true }));
    playBtn.addEventListener("click", () => {
      userPaused = !userPaused;
      if (userPaused) {
        renderState();
      } else {
        restartFill();
        renderState();
      }
    });
    segs.forEach((g, i) => g.addEventListener("click", () => go(i, { announce: true })));
    slides.forEach((s, i) =>
      s.addEventListener("click", () => {
        if (i !== index) go(i, { announce: true });
      }),
    );

    root.addEventListener("keydown", (e) => {
      if (e.altKey || e.ctrlKey || e.metaKey) return;
      if (e.key === "ArrowRight") go(index + 1, { announce: true });
      else if (e.key === "ArrowLeft") go(index - 1, { announce: true });
      else if (e.key === "Home") go(0, { announce: true });
      else if (e.key === "End") go(total - 1, { announce: true });
      else return;
      e.preventDefault();
    });

    // swipe or trackpad scroll: the card nearest the start edge becomes active
    track.addEventListener(
      "scroll",
      () => {
        window.clearTimeout(settleTimer);
        settleTimer = window.setTimeout(() => {
          if (programmatic) {
            programmatic = false;
            return;
          }
          const edge = track.scrollLeft + padStart();
          let best = index;
          let bestD = Infinity;
          slides.forEach((s, i) => {
            const d = Math.abs(s.offsetLeft - edge);
            if (d < bestD) {
              bestD = d;
              best = i;
            }
          });
          if (best !== index) {
            index = best;
            render();
            restartFill();
          }
        }, 140);
      },
      { passive: true },
    );

    root.addEventListener("mouseenter", () => {
      hoverPaused = true;
      renderState();
    });
    root.addEventListener("mouseleave", () => {
      hoverPaused = false;
      renderState();
    });
    root.addEventListener("focusin", () => {
      focusPaused = true;
      renderState();
    });
    root.addEventListener("focusout", (e) => {
      if (!root.contains(e.relatedTarget)) {
        focusPaused = false;
        renderState();
      }
    });

    if ("IntersectionObserver" in window) {
      new IntersectionObserver(
        (entries) => {
          offscreen = !entries[entries.length - 1].isIntersecting;
          renderState();
        },
        { threshold: 0.35 },
      ).observe(track);
    } else {
      offscreen = false;
    }

    let resizeTimer = 0;
    window.addEventListener("resize", () => {
      window.clearTimeout(resizeTimer);
      resizeTimer = window.setTimeout(() => scrollTo(index, false), 150);
    });
    onMQChange(reduceMQ, () => {
      if (reduced()) userPaused = true;
      restartFill();
      renderState();
    });

    go(0, { smooth: false });
  }

  // Behind-the-scenes carousel: buttons, arrow keys, and mouse drag.
  function initCarousel() {
    const root = document.querySelector("[data-carousel]");
    if (!root) return;
    const track = root.querySelector("[data-carousel-track]");
    const prev = root.querySelector("[data-carousel-prev]");
    const next = root.querySelector("[data-carousel-next]");
    root.querySelectorAll("[data-carousel-ui]").forEach((el) => {
      el.hidden = false;
    });
    track.classList.add("is-draggable");

    const stepSize = () => {
      const card = track.children[0];
      const gap = parseFloat(getComputedStyle(track).columnGap) || 0;
      return card.getBoundingClientRect().width + gap;
    };
    const by = (dir) => track.scrollBy({ left: dir * stepSize(), behavior: reduced() ? "auto" : "smooth" });
    const update = () => {
      prev.disabled = track.scrollLeft <= 4;
      next.disabled = track.scrollLeft + track.clientWidth >= track.scrollWidth - 4;
    };
    prev.addEventListener("click", () => by(-1));
    next.addEventListener("click", () => by(1));
    track.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
    update();

    track.addEventListener("keydown", (e) => {
      if (e.key === "ArrowRight") by(1);
      else if (e.key === "ArrowLeft") by(-1);
      else return;
      e.preventDefault();
    });

    let dragging = false;
    let moved = false;
    let startX = 0;
    let startLeft = 0;
    track.addEventListener("pointerdown", (e) => {
      if (e.pointerType !== "mouse" || e.button !== 0) return;
      dragging = true;
      moved = false;
      startX = e.clientX;
      startLeft = track.scrollLeft;
    });
    track.addEventListener("pointermove", (e) => {
      if (!dragging) return;
      const dx = e.clientX - startX;
      if (!moved && Math.abs(dx) > 5) {
        moved = true;
        track.classList.add("is-dragging");
        track.setPointerCapture(e.pointerId);
      }
      if (moved) track.scrollLeft = startLeft - dx;
    });
    const end = (e) => {
      if (!dragging) return;
      dragging = false;
      if (!moved) return;
      if (track.hasPointerCapture(e.pointerId)) track.releasePointerCapture(e.pointerId);
      // settle on the nearest card once snapping is back on
      const size = stepSize();
      const target = Math.round(track.scrollLeft / size) * size;
      track.classList.remove("is-dragging");
      track.scrollTo({ left: target, behavior: reduced() ? "auto" : "smooth" });
    };
    track.addEventListener("pointerup", end);
    track.addEventListener("pointercancel", end);
    track.addEventListener(
      "click",
      (e) => {
        if (moved) {
          e.preventDefault();
          e.stopPropagation();
          moved = false;
        }
      },
      true,
    );
  }

  // Copy buttons for the install blocks.
  function initCopy() {
    const status = document.querySelector("[data-copy-status]");
    for (const btn of document.querySelectorAll("[data-copy]")) {
      const source = document.querySelector(btn.getAttribute("data-copy"));
      if (!source) continue;
      btn.hidden = false;
      const original = btn.textContent;
      btn.addEventListener("click", async () => {
        const text = Array.from(source.querySelectorAll(".ln")).length
          ? Array.from(source.querySelectorAll(".ln"))
              .map((l) => l.textContent)
              .join("\n")
          : source.textContent.trim();
        let ok = false;
        try {
          await navigator.clipboard.writeText(text);
          ok = true;
        } catch {
          const area = document.createElement("textarea");
          area.value = text;
          area.setAttribute("readonly", "");
          area.style.position = "fixed";
          area.style.opacity = "0";
          document.body.appendChild(area);
          area.select();
          try {
            ok = document.execCommand("copy");
          } catch {
            ok = false;
          }
          area.remove();
        }
        btn.textContent = ok ? t.copied : t.copyFailed;
        btn.classList.toggle("is-done", ok);
        if (status) status.textContent = btn.textContent;
        window.setTimeout(() => {
          btn.textContent = original;
          btn.classList.remove("is-done");
        }, 2000);
      });
    }
  }

  // Mark the current document in the header, sidebar and footer.
  function markCurrent() {
    const page = document.body.dataset.page;
    for (const a of document.querySelectorAll(`[data-nav="${page}"]`)) a.setAttribute("aria-current", "page");
  }

  // Rows that scroll sideways (the phone header links, the how-it-works diagram) fade a cut
  // edge while more lies past it. The current page's link scrolls into view first.
  function initScrollFade() {
    for (const row of document.querySelectorAll(".nav-pages, .doc .diagram")) {
      const update = () => {
        const max = row.scrollWidth - row.clientWidth;
        row.classList.toggle("fade-start", max > 1 && row.scrollLeft > 1);
        row.classList.toggle("fade-end", max > 1 && row.scrollLeft < max - 1);
      };
      // the current link stops clear of the 40px fade, or at the end of the row
      const showCurrent = () => {
        const current = row.querySelector("[aria-current]");
        if (current) row.scrollLeft += Math.max(0, current.getBoundingClientRect().right - row.getBoundingClientRect().right + 40);
        update();
      };
      row.addEventListener("scroll", update, { passive: true });
      window.addEventListener("resize", update);
      showCurrent();
      if (document.fonts) document.fonts.ready.then(showCurrent);
    }
  }

  markCurrent();
  initScrollFade();
  initWall();
  initTyping();
  initEditDemo();
  initPhone();
  initShorts();
  initReel();
  initCarousel();
  initCopy();
})();
