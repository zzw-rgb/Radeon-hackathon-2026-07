import heroImage from "./assets/radeonvla-reflex-hero.png";
import {
  copy,
  demos,
  features,
  navItems,
  projectLinks,
  t,
  taskRows,
  type Locale,
  verifiedMetrics,
} from "./content";
import "./styles.css";

const app = document.querySelector<HTMLDivElement>("#app");

if (!app) {
  throw new Error("Missing #app mount point");
}

const localeKey = "radeonvla-reflex-locale";
const storedLocale = localStorage.getItem(localeKey);
let locale: Locale = storedLocale === "zh" ? "zh" : "en";

function iconArrow(): string {
  return '<span aria-hidden="true">↗</span>';
}

function render(): void {
  document.documentElement.lang = locale === "zh" ? "zh-CN" : "en";
  document.title = t(copy.pageTitle, locale);
  document.querySelector<HTMLAnchorElement>(".skip-link")!.textContent = t(copy.skipLink, locale);
  document.querySelector<HTMLMetaElement>('meta[name="description"]')!.content = t(copy.pageDescription, locale);

  app!.innerHTML = `
    <header class="site-header">
      <a class="wordmark" href="#top" aria-label="${t(copy.homeLabel, locale)}">
        <span class="wordmark-mark" aria-hidden="true"><i></i><i></i></span>
        <span>
          <strong>RadeonVLA</strong><em>Reflex</em>
          <small>${t(copy.brandKicker, locale)}</small>
        </span>
      </a>
      <nav class="site-nav" aria-label="${t(copy.primaryNav, locale)}">
        ${navItems.map((item) => `<a href="${item.href}">${t(item.label, locale)}</a>`).join("")}
      </nav>
      <div class="locale-switch" role="group" aria-label="${t(copy.languageLabel, locale)}">
        <button type="button" data-locale="en" aria-pressed="${locale === "en"}">EN</button>
        <span aria-hidden="true">/</span>
        <button type="button" data-locale="zh" aria-pressed="${locale === "zh"}">中</button>
      </div>
    </header>

    <main id="main">
      <section class="hero section-shell" id="top" aria-labelledby="hero-title">
        <div class="hero-grid">
          <div class="hero-copy reveal">
            <p class="badge"><span></span>${t(copy.heroBadge, locale)}</p>
            <h1 id="hero-title">
              <span>${t(copy.heroTitleA, locale)}</span>
              <em>${t(copy.heroTitleB, locale)}</em>
            </h1>
            <p class="hero-lede">${t(copy.heroBody, locale)}</p>
            <div class="hero-actions">
              <a class="button button-primary" href="${projectLinks.source}" target="_blank" rel="noreferrer">
                ${t(copy.sourceCta, locale)} ${iconArrow()}
              </a>
              <a class="button button-quiet" href="#demo">${t(copy.demoCta, locale)} <span aria-hidden="true">↓</span></a>
            </div>
          </div>
          <figure class="hero-visual reveal" aria-labelledby="hero-visual-caption">
            <div class="visual-orbit orbit-one" aria-hidden="true"></div>
            <div class="visual-orbit orbit-two" aria-hidden="true"></div>
            <img src="${heroImage}" alt="${t(copy.heroAlt, locale)}" />
            <figcaption id="hero-visual-caption">
              <span class="live-dot" aria-hidden="true"></span>
              ${t(copy.placeholder, locale)}
            </figcaption>
            <div class="telemetry-card telemetry-command" aria-hidden="true">
              <small>COMMAND SESSION</small>
              <strong>v2</strong>
              <span>stale chunk → invalid</span>
            </div>
            <div class="telemetry-card telemetry-state" aria-hidden="true">
              <small>RUNTIME STATE</small>
              <strong>INTERRUPTED</strong>
              <span>safe hold active</span>
            </div>
          </figure>
        </div>
        <div class="hero-index" aria-hidden="true">RVR—26</div>
      </section>

      <section class="proof-band" aria-labelledby="proof-heading">
        <div class="section-shell">
          <div class="proof-heading reveal">
            <p class="eyebrow" id="proof-heading">${t(copy.proofLabel, locale)}</p>
            <p>${t(copy.proofNote, locale)}</p>
          </div>
          <div class="metric-grid">
            ${verifiedMetrics
              .map(
                (metric) => `
                  <article class="metric reveal">
                    <strong>${metric.value}</strong>
                    <h2>${t(metric.label, locale)}</h2>
                    <p>${t(metric.detail, locale)}</p>
                  </article>`,
              )
              .join("")}
          </div>
        </div>
      </section>

      <section class="demo section-shell section-block" id="demo" aria-labelledby="demo-title">
        <div class="section-intro reveal">
          <p class="eyebrow">${t(copy.sectionDemoKicker, locale)}</p>
          <h2 id="demo-title">${t(copy.sectionDemoTitle, locale)}</h2>
          <p>${t(copy.sectionDemoBody, locale)}</p>
        </div>
        <div class="video-placeholder reveal" role="status">
          <div class="video-grid" aria-hidden="true"></div>
          <div class="video-status">
            <span class="play-symbol" aria-hidden="true">▶</span>
            <div>
              <small>${t(copy.videoLabel, locale)}</small>
              <strong>${t(copy.videoPending, locale)}</strong>
              <p>${t(copy.videoBody, locale)}</p>
            </div>
          </div>
          <span class="pending-pill">${t(copy.pending, locale)}</span>
        </div>
        <div class="demo-grid">
          ${demos
            .map(
              (demo) => `
                <article class="demo-card reveal">
                  <div class="demo-card-top">
                    <span>${demo.index}</span>
                    <span class="state state-${demo.state.toLowerCase()}">${demo.state}</span>
                  </div>
                  <div class="signal" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></div>
                  <p class="eyebrow">${t(copy.plannedEvidence, locale)}</p>
                  <h3>${t(demo.title, locale)}</h3>
                  <p>${t(demo.body, locale)}</p>
                  <code>${t(demo.event, locale)}</code>
                </article>`,
            )
            .join("")}
        </div>
      </section>

      <section class="runtime section-block" id="runtime" aria-labelledby="runtime-title">
        <div class="section-shell">
          <div class="section-intro reveal">
            <p class="eyebrow">${t(copy.runtimeKicker, locale)}</p>
            <h2 id="runtime-title">${t(copy.runtimeTitle, locale)}</h2>
            <p>${t(copy.runtimeBody, locale)}</p>
          </div>
          <div class="architecture reveal" aria-label="${t(copy.architectureLabel, locale)}">
            <div class="architecture-track" aria-hidden="true"></div>
            <div class="architecture-node input-node">
              <span>INPUT</span>
              <strong>${t(copy.architectureInput, locale)}</strong>
            </div>
            <span class="architecture-arrow" aria-hidden="true">→</span>
            <div class="architecture-node policy-node">
              <span>LEARNED</span>
              <strong>${t(copy.architecturePolicy, locale)}</strong>
            </div>
            <span class="architecture-arrow" aria-hidden="true">→</span>
            <div class="architecture-node reflex-node">
              <span>DETERMINISTIC</span>
              <strong>${t(copy.architectureReflex, locale)}</strong>
              <small>${t(copy.architectureSafety, locale)}</small>
            </div>
            <span class="architecture-arrow" aria-hidden="true">→</span>
            <div class="architecture-node sim-node">
              <span>CONTROL</span>
              <strong>${t(copy.architectureSim, locale)}</strong>
            </div>
          </div>
          <div class="feature-grid">
            ${features
              .map(
                (feature) => `
                  <article class="feature reveal">
                    <p class="eyebrow">${feature.eyebrow}</p>
                    <h3>${t(feature.title, locale)}</h3>
                    <p>${t(feature.body, locale)}</p>
                  </article>`,
              )
              .join("")}
          </div>
        </div>
      </section>

      <section class="benchmark section-shell section-block" id="benchmark" aria-labelledby="benchmark-title">
        <div class="section-intro reveal">
          <p class="eyebrow">${t(copy.benchmarkKicker, locale)}</p>
          <h2 id="benchmark-title">${t(copy.benchmarkTitle, locale)}</h2>
          <p>${t(copy.benchmarkBody, locale)}</p>
        </div>
        <div class="task-table-wrap reveal" tabindex="0" role="region" aria-label="L1 task matrix">
          <table class="task-table">
            <thead>
              <tr>
                <th scope="col">${t(copy.objectLabel, locale)}</th>
                <th scope="col">${t(copy.targetLabel, locale)} 01</th>
                <th scope="col">${t(copy.targetLabel, locale)} 02</th>
                <th scope="col">${t(copy.targetLabel, locale)} 03</th>
                <th scope="col">${t(copy.targetLabel, locale)} 04</th>
              </tr>
            </thead>
            <tbody>
              ${taskRows
                .map(
                  (row, rowIndex) => `
                    <tr>
                      <th scope="row"><span class="fruit-index">0${rowIndex + 1}</span>${t(row.fruit, locale)}</th>
                      ${row.targets
                        .map(
                          (target) => `
                            <td>
                              <span class="bowl bowl-${target.color}" aria-hidden="true"></span>
                              ${t(target.label, locale)}
                              <small>${t(copy.demosLabel, locale)}</small>
                            </td>`,
                        )
                        .join("")}
                    </tr>`,
                )
                .join("")}
            </tbody>
          </table>
        </div>
      </section>

      <section class="evidence section-block" aria-labelledby="evidence-title">
        <div class="section-shell">
          <div class="section-intro reveal">
            <p class="eyebrow">${t(copy.evidenceKicker, locale)}</p>
            <h2 id="evidence-title">${t(copy.evidenceTitle, locale)}</h2>
            <p>${t(copy.evidenceBody, locale)}</p>
          </div>
          <div class="pending-results">
            ${copy.resultLabels
              .map(
                (label, index) => `
                  <article class="pending-result reveal">
                    <span>0${index + 1}</span>
                    <h3>${t(label, locale)}</h3>
                    <strong>${t(copy.pending, locale)}</strong>
                    <p>${t(copy.resultPendingNote, locale)}</p>
                  </article>`,
              )
              .join("")}
          </div>
          <div class="release-grid">
            <article class="release-card release-target reveal">
              <p class="eyebrow">${t(copy.releaseTarget, locale)}</p>
              <h3>${t(copy.releaseTargetValue, locale)}</h3>
              <p>${t(copy.releaseTargetBody, locale)}</p>
              <span class="pending-pill">${t(copy.pending, locale)}</span>
            </article>
            <article class="release-card release-model reveal">
              <p class="eyebrow">${t(copy.modelLabel, locale)}</p>
              <h3>${t(copy.modelValue, locale)}</h3>
              <p>${t(copy.modelBody, locale)}</p>
              <a href="${projectLinks.baseModel}" target="_blank" rel="noreferrer">
                ${t(copy.baseModelCta, locale)} ${iconArrow()}
              </a>
            </article>
          </div>
        </div>
      </section>

      <section class="reproduce section-shell section-block" id="reproduce" aria-labelledby="reproduce-title">
        <div class="reproduce-grid">
          <div class="section-intro reveal">
            <p class="eyebrow">${t(copy.reproduceKicker, locale)}</p>
            <h2 id="reproduce-title">${t(copy.reproduceTitle, locale)}</h2>
            <p>${t(copy.reproduceBody, locale)}</p>
          </div>
          <ol class="pipeline reveal">
            ${copy.pipelineSteps
              .map(
                (step, index) => `
                  <li>
                    <span>${String(index + 1).padStart(2, "0")}</span>
                    <strong>${t(step, locale)}</strong>
                  </li>`,
              )
              .join("")}
          </ol>
        </div>
        <div class="command-panel reveal">
          <div>
            <span class="terminal-dots" aria-hidden="true"><i></i><i></i><i></i></span>
            <small>${t(copy.commandLabel, locale)}</small>
          </div>
          <code><span>$</span> python -m pytest -q<br /><span>$</span> python -m ruff check src tests<br /><span>$</span> python -m radeonvla.submission_audit</code>
        </div>
        <aside class="limitation reveal">
          <strong>${t(copy.limitationLabel, locale)}</strong>
          <p>${t(copy.limitationBody, locale)}</p>
        </aside>
      </section>

      <section class="team section-block" aria-labelledby="team-title">
        <div class="section-shell team-inner reveal">
          <div>
            <p class="eyebrow">${t(copy.teamKicker, locale)}</p>
            <h2 id="team-title">${t(copy.teamTitle, locale)}</h2>
            <p>${t(copy.teamBody, locale)}</p>
          </div>
          <div class="team-actions">
            <a class="button button-light" href="${projectLinks.contest}" target="_blank" rel="noreferrer">
              ${t(copy.contestCta, locale)} ${iconArrow()}
            </a>
            <a class="button button-outline-light" href="${projectLinks.source}" target="_blank" rel="noreferrer">
              GitHub ${iconArrow()}
            </a>
          </div>
        </div>
      </section>
    </main>

    <footer class="site-footer section-shell">
      <p>${t(copy.footer, locale)}</p>
      <p>${t(copy.attribution, locale)}</p>
    </footer>
  `;

  bindLocaleControls();
  enableReveal();
}

function bindLocaleControls(): void {
  document.querySelectorAll<HTMLButtonElement>("[data-locale]").forEach((button) => {
    button.addEventListener("click", () => {
      const nextLocale = button.dataset.locale;
      if (nextLocale !== "en" && nextLocale !== "zh") return;
      locale = nextLocale;
      localStorage.setItem(localeKey, locale);
      render();
    });
  });
}

function enableReveal(): void {
  const items = document.querySelectorAll<HTMLElement>(".reveal");

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches || !("IntersectionObserver" in window)) {
    items.forEach((item) => item.classList.add("is-visible"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    },
    { rootMargin: "0px 0px -8%", threshold: 0.08 },
  );

  items.forEach((item) => observer.observe(item));
}

render();
