/* SuplaStock Landing — GSAP Animations
   Requires: gsap@3, ScrollTrigger, SplitText (optional)
   ---------------------------------------------------- */

gsap.registerPlugin(ScrollTrigger);

/* ─── Helpers ─── */
const ease = "power3.out";

/* ─── 1. NAVBAR entrance ─── */
gsap.from("header", {
  yPercent: -100,
  opacity: 0,
  duration: 0.7,
  ease,
});

/* ─── 2. HERO — staggered elements ─── */
const heroTl = gsap.timeline({ defaults: { ease, duration: 0.8 } });

heroTl
  .from(".hero-badge",      { opacity: 0, y: 24 })
  .from(".hero-title",      { opacity: 0, y: 40 },      "-=0.5")
  .from(".hero-subtitle",   { opacity: 0, y: 30 },      "-=0.5")
  .from(".hero-cta-group",  { opacity: 0, y: 24 },      "-=0.45")
  .from(".hero-social-proof", { opacity: 0, y: 16 },    "-=0.4")
  .from(".hero-mockup",     { opacity: 0, x: 60, scale: 0.96 }, "-=0.6");

/* Floating badge — subtle float loop */
gsap.to(".hero-floating-badge", {
  y: -10,
  duration: 1.8,
  ease: "sine.inOut",
  repeat: -1,
  yoyo: true,
});

/* ─── 3. VALUE PROP NUMBERS — counter + slide up ─── */
gsap.utils.toArray(".stat-card").forEach((card, i) => {
  gsap.from(card, {
    scrollTrigger: { trigger: card, start: "top 88%", toggleActions: "play none none none" },
    opacity: 0,
    y: 40,
    duration: 0.7,
    delay: i * 0.12,
    ease,
  });

  /* Number counter animation */
  const numEl = card.querySelector(".stat-number");
  if (!numEl) return;

  const raw     = numEl.dataset.target || numEl.textContent.trim();
  const isPlus  = raw.includes("+");
  const isPct   = raw.includes("%");
  const suffix  = isPlus ? "+" : isPct ? "%" : "";
  const numeric = parseFloat(raw.replace(/[^0-9.]/g, ""));

  if (isNaN(numeric)) return;

  ScrollTrigger.create({
    trigger: card,
    start: "top 88%",
    once: true,
    onEnter: () => {
      gsap.fromTo(
        { val: 0 },
        { val: numeric, duration: 1.6, ease: "power2.out",
          onUpdate() { numEl.textContent = Math.round(this.targets()[0].val) + suffix; }
        }
      );
    },
  });
});

/* ─── 4. FEATURE CARDS — scroll stagger ─── */
gsap.utils.toArray(".feature-ui-card").forEach((card, i) => {
  gsap.from(card, {
    scrollTrigger: {
      trigger: card,
      start: "top 85%",
      toggleActions: "play none none none",
    },
    opacity: 0,
    y: 50,
    duration: 0.75,
    delay: (i % 2) * 0.15,
    ease,
  });
});

/* ─── 5. PROCESS STEPS ─── */
gsap.utils.toArray(".process-step").forEach((step, i) => {
  gsap.from(step, {
    scrollTrigger: { trigger: step, start: "top 88%", toggleActions: "play none none none" },
    opacity: 0,
    y: 36,
    scale: 0.95,
    duration: 0.65,
    delay: i * 0.13,
    ease,
  });
});

/* ─── 6. METRICS (social proof row) ─── */
gsap.utils.toArray(".metric-item").forEach((el, i) => {
  gsap.from(el, {
    scrollTrigger: { trigger: el, start: "top 90%", toggleActions: "play none none none" },
    opacity: 0,
    x: i % 2 === 0 ? -30 : 30,
    duration: 0.6,
    delay: i * 0.1,
    ease,
  });
});

/* ─── 7. TESTIMONIAL CARDS — stagger ─── */
gsap.from(".testimonial-card", {
  scrollTrigger: {
    trigger: ".testimonials-grid",
    start: "top 85%",
    toggleActions: "play none none none",
  },
  opacity: 0,
  y: 40,
  duration: 0.65,
  stagger: 0.15,
  ease,
});

/* ─── 8. FINAL CTA block ─── */
gsap.from(".final-cta-block", {
  scrollTrigger: { trigger: ".final-cta-block", start: "top 85%" },
  opacity: 0,
  scale: 0.97,
  y: 30,
  duration: 0.8,
  ease,
});

/* ─── 9. FOOTER links — fade up ─── */
gsap.from("footer", {
  scrollTrigger: { trigger: "footer", start: "top 92%" },
  opacity: 0,
  y: 20,
  duration: 0.6,
  ease,
});

/* ─── 10. Parallax on hero mockup (subtle) ─── */
gsap.to(".hero-mockup", {
  scrollTrigger: {
    trigger: "body",
    start: "top top",
    end: "500px top",
    scrub: 1,
  },
  y: 40,
  ease: "none",
});
