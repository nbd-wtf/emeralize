'use strict'

const HSBsDropdown = {
  init(options) {
    this.setAnimations()
    this.openOnHover()
  },

  setAnimations() {
    window.addEventListener('show.bs.dropdown', el => {
      const animation = el.target.hasAttribute('data-bs-dropdown-animation')
      if (!animation) return

      const menu = el.target.nextElementSibling
      menu.style.opacity = 0
      setTimeout(() => {
        menu.style.transform = `${menu.style.transform} translateY(10px)`
      })
      setTimeout(() => {
        menu.style.transform = `${menu.style.transform} translateY(-10px)`
        menu.style.transition = 'transform 300ms, opacity 300ms'
        menu.style.opacity = 1
      }, 100)
    })

    window.addEventListener('hide.bs.dropdown', el => {
      const animation = el.target.hasAttribute('data-bs-dropdown-animation')
      if (!animation) return

      const menu = el.target.nextElementSibling
      setTimeout(() => {
        menu.style.removeProperty('transform')
        menu.style.removeProperty('transition')
      })
    })
  },

  openOnHover() {
    const $targets = Array.from(document.querySelectorAll('[data-bs-open-on-hover]'))

    $targets.forEach($target => {
      var timeout
      const instance = new bootstrap.Dropdown($target)

      function close() {
        timeout = setTimeout(() => {
          instance.hide()
        }, 500)
      }

      $target.addEventListener('mouseenter', () => {
        clearTimeout(timeout)
        instance.show()
      })

      instance._menu.addEventListener('mouseenter', () => {
        window.clearTimeout(timeout)
      })

      Array.from([instance._menu, $target]).forEach($el => $el.addEventListener('mouseleave', close))
    })
  }
}
