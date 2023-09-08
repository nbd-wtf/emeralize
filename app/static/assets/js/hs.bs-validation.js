'use strict'

const validators = {
  'data-hs-validation-equal-field': field => {
    const equalTarget = document.querySelector(field.getAttribute('data-hs-validation-equal-field'))

    field.addEventListener('input', e => {
      equalTarget.value.toString().toLocaleLowerCase() !== e.target.value.toString().toLocaleLowerCase() ? field.setCustomValidity('qual-field') : field.setCustomValidity('')
      HSBsValidation.updateFieldStete(field)
    })

    equalTarget.addEventListener('input', e => {
      field.value.toString().toLocaleLowerCase() !== e.target.value.toString().toLocaleLowerCase() ? field.setCustomValidity('qual-field') : field.setCustomValidity('')
      HSBsValidation.updateFieldStete(field)
    })
  }
}

const HSBsValidation = {
  init(selector, options) {
    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    var forms = document.querySelectorAll(selector)

    // Loop over them and prevent submission
    Array.prototype.slice.call(forms)
      .forEach((form) => {
        for (const validator in validators) {
          Array.prototype.slice.call(form.querySelectorAll(`[${validator}]`))
            .forEach(validators[validator])
        }

        this.addVlidationListners(form.elements)

        form.addEventListener('submit', event => {
          if (!form.checkValidity()) {
            event.preventDefault()
            event.stopPropagation()
            this.checkFieldsState(form.elements)
          } else {
            this.onSubmit({event, form, options})
          }

          form.classList.add('was-validated')
        }, false)
      })

    return this
  },

  addVlidationListners(elements) {
    Array.prototype.slice.call(elements)
      .forEach(field => {
        const target = field.closest('[data-hs-validation-validate-class]')
        if (!target) return

        field.addEventListener('input', e => this.updateFieldStete(e.target))
        field.addEventListener('focus', e => target.classList.add('focus'))
        field.addEventListener('blur', e => target.classList.remove('focus'))
      })
  },

  checkFieldsState(elements) {
    Array.prototype.slice.call(elements)
      .forEach(field => this.updateFieldStete(field))
  },

  updateFieldStete(field) {
    const target = field.closest('[data-hs-validation-validate-class]')
    if (!target) return

    if (field.checkValidity()) {
      target.classList.add('is-valid')
      target.classList.remove('is-invalid')
    } else {
      target.classList.add('is-invalid')
      target.classList.remove('is-valid')
    }
  },

  onSubmit(data) {
    if (!data.options || typeof data.options.onSubmit !== 'function') return false
    return data.options.onSubmit(data)
  }
}
