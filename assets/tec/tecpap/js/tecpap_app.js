document.addEventListener('alpine:init', () => {
  Alpine.data('tecPapApp', () => ({
    currentView: 'landing',
    currentForm: null,
    formData: { name: '', email: '', description: '' },

    init() {
      console.log('tecPap started');
    },

    openForm(formId) {
      this.currentForm = formId;
      this.formData = { name: '', email: '', description: '' };
      this.currentView = 'form';
    },

    goBack() {
      this.currentView = 'landing';
      this.currentForm = null;
    },

    submitForm() {
      this.currentView = 'preview';
    },

    editForm() {
      this.currentView = 'form';
    },

    confirmSubmit() {
      fetch('/api/tecpap/form/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          form_name: this.currentForm,
          form_data: this.formData
        })
      })
      .then(res => {
        if (!res.ok) throw new Error("خطا در ارسال فرم");
        return res.json();
      })
      .then(() => {
        this.currentView = 'success';
      })
      .catch(err => alert(err.message));
    },

    returnHome() {
      this.goBack();
    }
  }))
});
