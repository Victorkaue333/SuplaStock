(function () {
    'use strict';

    const TEXT_TRIGGER_TYPES = new Set([
        'text',
        'search',
        'email',
        'tel',
        'url',
        'number',
    ]);
    const CHANGE_TRIGGER_TYPES = new Set([
        'date',
        'month',
        'week',
        'time',
        'datetime-local',
        'checkbox',
        'radio',
    ]);
    const DEBOUNCE_DEFAULT = 420;
    const timerByControl = new WeakMap();

    function parseBoolean(rawValue, fallback) {
        if (rawValue == null || rawValue === '') {
            return fallback;
        }
        return ['1', 'true', 'yes', 'on'].includes(String(rawValue).trim().toLowerCase());
    }

    function getNamedControls(form) {
        return Array.from(form.elements || []).filter((element) => {
            if (!element || !element.name || element.disabled) {
                return false;
            }
            const type = String(element.type || '').toLowerCase();
            return !['submit', 'button', 'reset', 'image', 'file'].includes(type);
        });
    }

    function removePaginationParams(params) {
        Array.from(params.keys()).forEach((key) => {
            if (key === 'page' || /_page$/i.test(key)) {
                params.delete(key);
            }
        });
    }

    function buildMergedParams(form) {
        const params = new URLSearchParams(window.location.search);
        removePaginationParams(params);

        const controls = getNamedControls(form);
        const fieldNames = new Set(controls.map((control) => control.name));
        fieldNames.forEach((name) => params.delete(name));

        const formData = new FormData(form);
        for (const [name, rawValue] of formData.entries()) {
            const value = typeof rawValue === 'string' ? rawValue.trim() : rawValue;
            if (value === '' || value == null) {
                continue;
            }
            params.append(name, value);
        }
        return params;
    }

    function normalizeQuery(params) {
        const normalized = new URLSearchParams(params.toString());
        removePaginationParams(normalized);
        return normalized.toString();
    }

    function getFormActionPath(form) {
        const rawAction = (form.getAttribute('action') || window.location.pathname || '').trim();
        if (!rawAction) {
            return window.location.pathname;
        }
        return rawAction.split('#')[0].split('?')[0];
    }

    function submitFilterForm(form) {
        if (form.dataset.filterSubmitting === '1') {
            return;
        }

        const targetParams = buildMergedParams(form);
        const currentQuery = normalizeQuery(new URLSearchParams(window.location.search));
        const targetQuery = normalizeQuery(targetParams);
        if (targetQuery === currentQuery) {
            return;
        }

        form.dataset.filterSubmitting = '1';
        const actionPath = getFormActionPath(form);
        const targetUrl = targetQuery ? `${actionPath}?${targetQuery}` : actionPath;
        window.location.assign(targetUrl);
    }

    function getDebounceDelay(form, control) {
        const controlDelay = Number.parseInt(control.dataset.filterDebounce || '', 10);
        if (Number.isFinite(controlDelay) && controlDelay >= 0) {
            return controlDelay;
        }
        const formDelay = Number.parseInt(form.dataset.filterDebounce || '', 10);
        if (Number.isFinite(formDelay) && formDelay >= 0) {
            return formDelay;
        }
        return DEBOUNCE_DEFAULT;
    }

    function inferTrigger(control) {
        const explicit = String(control.dataset.filterTrigger || '').trim().toLowerCase();
        if (explicit) {
            return explicit;
        }

        const tagName = control.tagName.toLowerCase();
        if (tagName === 'select') {
            return 'change';
        }
        if (tagName === 'textarea') {
            return 'input';
        }

        if (tagName === 'input') {
            const type = String(control.type || 'text').toLowerCase();
            if (type === 'hidden') {
                return '';
            }
            if (TEXT_TRIGGER_TYPES.has(type)) {
                return 'input';
            }
            if (CHANGE_TRIGGER_TYPES.has(type)) {
                return 'change';
            }
        }
        return '';
    }

    function queueDebouncedSubmit(form, control) {
        const existingTimer = timerByControl.get(control);
        if (existingTimer) {
            window.clearTimeout(existingTimer);
        }

        const nextTimer = window.setTimeout(() => {
            submitFilterForm(form);
        }, getDebounceDelay(form, control));
        timerByControl.set(control, nextTimer);
    }

    function bindAutoSubmit(form) {
        const autoSubmitEnabled = parseBoolean(form.dataset.autoSubmit, false);
        if (!autoSubmitEnabled) {
            return;
        }

        const controls = getNamedControls(form).filter((control) => String(control.type || '').toLowerCase() !== 'hidden');
        controls.forEach((control) => {
            const trigger = inferTrigger(control);
            if (trigger === 'input') {
                control.addEventListener('input', () => queueDebouncedSubmit(form, control));
                control.addEventListener('keydown', (event) => {
                    if (event.key !== 'Enter') {
                        return;
                    }
                    event.preventDefault();
                    const existingTimer = timerByControl.get(control);
                    if (existingTimer) {
                        window.clearTimeout(existingTimer);
                    }
                    submitFilterForm(form);
                });
                return;
            }

            if (trigger === 'change') {
                control.addEventListener('change', () => submitFilterForm(form));
            }
        });
    }

    function bindFilterForm(form) {
        form.addEventListener('submit', (event) => {
            event.preventDefault();
            submitFilterForm(form);
        });

        bindAutoSubmit(form);
    }

    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('form[data-filter-form]').forEach((form) => {
            bindFilterForm(form);
        });
    });
})();

