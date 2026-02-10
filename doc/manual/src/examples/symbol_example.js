/**
 * Example JavaScript module for symbol extraction.
 */

function formatDate(date) {
    return date.toISOString().split('T')[0];
}

class EventEmitter {
    constructor() {
        this.listeners = {};
    }

    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }

    emit(event, data) {
        const handlers = this.listeners[event] || [];
        handlers.forEach(fn => fn(data));
    }
}

const MAX_RETRIES = 3;
