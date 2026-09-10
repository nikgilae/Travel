import { useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { ymGoal } from '../utils/metrika'
import './LandingPage.css'

function StarIcon() {
  return (
    <svg viewBox="0 0 12 12" aria-hidden="true">
      <path d="M6 .8l1.6 3.3 3.6.5-2.6 2.6.6 3.6L6 9.1l-3.2 1.7.6-3.6L.8 4.6l3.6-.5z" />
    </svg>
  )
}

export default function LandingPage() {
  const rootRef = useRef(null)
  const s4Ref = useRef(null)

  // Оркестрация анимаций из final.html: раскрытие секций по IntersectionObserver
  // и перестроение дня на экране 4. Перенесено дословно из ванильного <script>.
  useEffect(() => {
    const root = rootRef.current
    const s4 = s4Ref.current
    if (!root || !s4) return undefined

    const timers = []
    const observers = []

    function flip() {
      const hide = s4.querySelectorAll('.swap .a, .roll i:first-child')
      const show = s4.querySelectorAll('.swap .b, .roll i:last-child')
      for (let i = 0; i < hide.length; i++) hide[i].setAttribute('aria-hidden', 'true')
      for (let j = 0; j < show.length; j++) show[j].removeAttribute('aria-hidden')
    }

    function rebuild() {
      if (s4.classList.contains('talk')) return
      s4.classList.add('talk')
      const t = setTimeout(function () {
        s4.classList.add('done')
        flip()
      }, 780)
      timers.push(t)
    }

    const calm = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches

    if (calm) {
      const all = root.querySelectorAll('.s')
      for (let i = 0; i < all.length; i++) all[i].classList.add('on')
      s4.classList.add('talk', 'done')
      flip()
      return undefined
    }

    if (!('IntersectionObserver' in window)) {
      const ss = root.querySelectorAll('.s')
      for (let j = 0; j < ss.length; j++) ss[j].classList.add('on')
      rebuild()
      return function cleanup() {
        timers.forEach(clearTimeout)
      }
    }

    const reveal = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return
        e.target.classList.add('on')
        reveal.unobserve(e.target)
      })
    }, { rootMargin: '0px 0px -18% 0px', threshold: 0.01 })
    observers.push(reveal)

    const acts = root.querySelectorAll('.s:not(.s1)')
    for (let k = 0; k < acts.length; k++) reveal.observe(acts[k])

    const scene = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.intersectionRatio < 0.45) return
        scene.unobserve(e.target)
        const t = setTimeout(rebuild, 620)
        timers.push(t)
      })
    }, { threshold: [0.45] })
    observers.push(scene)
    scene.observe(s4)

    return function cleanup() {
      timers.forEach(clearTimeout)
      observers.forEach(o => o.disconnect())
    }
  }, [])

  return (
    <div className="tr-landing" ref={rootRef}>
      <noscript>
        <style>{`
          .tr-landing .r,.tr-landing .cell{opacity:1;transform:none}
          .tr-landing .bub{opacity:1;transform:none}
          .tr-landing .swap .b{display:none}
        `}</style>
      </noscript>

      <main>

        <section className="s s1 on">
          <div className="fold col">

            <div className="brand r" style={{ '--d': '.05s' }}>TourRhythm</div>

            <div className="gap" style={{ '--g': 1.15, '--m': '18px' }}></div>

            <h1 className="q">
              <span className="ln"><i>Что ты будешь</i></span>
              <span className="ln"><i>делать в поездке</i></span>
              <span className="ln"><i>каждый день?</i></span>
            </h1>

            <p className="lede r" style={{ '--d': '.44s' }}>
              <b>Ответишь на несколько вопросов про даты, интересы, бюджет и компанию.</b>
              <b>Маршрут соберётся по дням из мест, которые реально существуют.</b>
            </p>

            <div className="gap" style={{ '--g': 1.42, '--m': '26px' }}></div>

            <Link className="cta r" style={{ '--d': '.58s' }} to="/onboarding" onClick={() => ymGoal('cta_top')}>Собрать маршрут</Link>
            <p className="alt r" style={{ '--d': '.66s' }}>Уже есть аккаунт → <Link to="/login">Войти</Link></p>

            <div className="gap" style={{ '--g': .55, '--m': '16px' }}></div>

            <div className="hint r" style={{ '--d': '.8s' }} aria-hidden="true"><i></i></div>

          </div>
        </section>

        <section className="s s2">
          <div className="col">
            <h2 className="h r">Маршрут на каждый день.</h2>

            <section className="board r" style={{ '--d': '.1s' }} aria-label="Пример маршрута по Стамбулу">
              <div className="bhead">
                <span className="d">Стамбул</span>
                <span className="c">4 дня</span>
              </div>

              <div className="daylab cell" style={{ '--i': 0 }}>День 1</div>
              <ul className="rows">
                <li className="row" style={{ '--i': 1 }}>
                  <span className="t cell">09:30</span>
                  <span className="rb cell"><span className="nm">Айя-София</span><span className="cat">музей</span></span>
                  <span className="rt cell"><StarIcon />4.7</span>
                </li>
                <li className="row" style={{ '--i': 2 }}>
                  <span className="t cell">12:00</span>
                  <span className="rb cell"><span className="nm">Гранд-базар</span><span className="cat">рынок</span></span>
                  <span className="rt cell"><StarIcon />4.4</span>
                </li>
                <li className="row" style={{ '--i': 3 }}>
                  <span className="t cell">15:30</span>
                  <span className="rb cell"><span className="nm">Цистерна Базилика</span><span className="cat">музей</span></span>
                  <span className="rt cell"><StarIcon />4.6</span>
                </li>
                <li className="row" style={{ '--i': 4 }}>
                  <span className="t cell">19:00</span>
                  <span className="rb cell"><span className="nm">Галатский мост</span><span className="cat">набережная</span></span>
                  <span className="rt cell"><StarIcon />4.5</span>
                </li>
              </ul>

              <div className="daylab cell" style={{ '--i': 5 }}>День 2</div>
              <ul className="rows">
                <li className="row" style={{ '--i': 6 }}>
                  <span className="t cell">10:00</span>
                  <span className="rb cell"><span className="nm">Дворец Топкапы</span><span className="cat">дворец</span></span>
                  <span className="rt cell"><StarIcon />4.6</span>
                </li>
                <li className="row" style={{ '--i': 7 }}>
                  <span className="t cell">14:00</span>
                  <span className="rb cell"><span className="nm">Ортакёй</span><span className="cat">район</span></span>
                  <span className="rt cell"><StarIcon />4.5</span>
                </li>
              </ul>
            </section>

            <p className="cap r" style={{ '--d': '.16s' }}>Стамбул, четыре дня. Собрался за пятнадцать секунд.</p>
          </div>
        </section>

        <section className="s s3">
          <div className="col">
            <h2 className="h r">Места настоящие.</h2>
            <p className="sub r" style={{ '--d': '.08s' }}>Не сгенерированный список названий. Координаты, часы работы и рейтинг берутся из Google&nbsp;Places. Открой любое место в картах и проверь.</p>

            <article className="card r" style={{ '--d': '.16s' }} aria-label="Карточка места: Айя-София">
              <div className="pname">Айя-София</div>
              <div className="pmeta">
                <span className="rt"><StarIcon />4.7</span>
                <span className="pdot" aria-hidden="true"></span>
                <span>музей</span>
              </div>
              <div className="crow">
                <svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="7.2" /><path d="M10 5.8V10l2.9 1.9" /></svg>
                <span>09:00 – 18:30</span>
              </div>
              <div className="crow">
                <svg viewBox="0 0 20 20" aria-hidden="true"><path d="M10 17.5s5.6-4.7 5.6-9a5.6 5.6 0 1 0-11.2 0c0 4.3 5.6 9 5.6 9z" /><circle cx="10" cy="8.4" r="2.1" /></svg>
                <span>41.0086, 28.9802</span>
              </div>
              <div className="cfoot">
                <span>Открыть в картах</span>
                <svg viewBox="0 0 20 20" aria-hidden="true"><path d="M6.6 13.4L13.4 6.6M7.4 6.6h6v6" /></svg>
              </div>
            </article>
          </div>
        </section>

        <section className="s s4" ref={s4Ref}>
          <div className="col">
            <h2 className="h r">Планы поменялись.</h2>
            <p className="sub r" style={{ '--d': '.08s' }}>Скажи агенту, что не так. Он перестроит день, сохранив логику всей поездки.</p>

            <div className="chat"><p className="bub">Убери музеи, добавь местную кухню</p></div>

            <section className="board r" style={{ '--d': '.16s' }} aria-label="День 1 до и после правки">
              <div className="bhead">
                <span className="d">День 1</span>
                <span className="c">Стамбул</span>
              </div>
              <ul className="rows">
                <li className="row" style={{ '--i': 1 }}>
                  <span className="t cell"><span className="roll"><u><i>09:30</i><i aria-hidden="true">10:00</i></u></span></span>
                  <span className="swap cell">
                    <span className="a"><span className="nm">Айя-София</span><span className="cat">музей</span></span>
                    <span className="b" aria-hidden="true"><span className="nm">Рыбный рынок Кадыкёя</span><span className="cat">рынок</span></span>
                  </span>
                </li>
                <li className="row" style={{ '--i': 2 }}>
                  <span className="t cell"><span className="roll"><u><i>12:00</i><i aria-hidden="true">12:30</i></u></span></span>
                  <span className="rb cell"><span className="nm">Гранд-базар</span><span className="cat">рынок</span></span>
                </li>
                <li className="row" style={{ '--i': 3 }}>
                  <span className="t cell"><span className="roll"><u><i>15:30</i><i aria-hidden="true">15:00</i></u></span></span>
                  <span className="swap late cell">
                    <span className="a"><span className="nm">Цистерна Базилика</span><span className="cat">музей</span></span>
                    <span className="b" aria-hidden="true"><span className="nm">Чия Софрасы</span><span className="cat">ресторан</span></span>
                  </span>
                </li>
                <li className="row" style={{ '--i': 4 }}>
                  <span className="t cell">19:00</span>
                  <span className="rb cell"><span className="nm">Галатский мост</span><span className="cat">набережная</span></span>
                </li>
              </ul>
            </section>
          </div>
        </section>

        <section className="s s5">
          <div className="col">
            <h2 className="h r">Собери первый день прямо сейчас.</h2>
            <p className="sub r" style={{ '--d': '.08s' }}>План от эксперта по стране, который говорит с тобой и перестраивает маршрут под твои интересы.</p>
            <div className="gap" style={{ '--g': 0, '--m': 'clamp(28px, 5svh, 44px)' }}></div>
            <Link className="cta r" style={{ '--d': '.16s' }} to="/onboarding" onClick={() => ymGoal('cta_bottom')}>Собрать маршрут</Link>
            <p className="alt r" style={{ '--d': '.22s' }}>Уже есть аккаунт → <Link to="/login">Войти</Link></p>
          </div>
        </section>

      </main>
    </div>
  )
}
