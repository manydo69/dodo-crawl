(() => {
    // thêm đoạn hook này vào snippets
    const original = CanvasRenderingContext2D.prototype.drawImage;
    const logs = [];

    console.log("[HOOK] Overriding drawImage...");
    CanvasRenderingContext2D.prototype.drawImage = function (...args) {
        try {
            const img = args[0];
            if (img && img.src) {
                if (args.length === 3) {
                    logs.push({ src: img.src, dx: args[1], dy: args[2] });
                } else if (args.length === 5) {
                    logs.push({
                        src: img.src,
                        dx: args[1],
                        dy: args[2],
                        dWidth: args[3],
                        dHeight: args[4],
                    });
                } else if (args.length === 9) {
                    logs.push({
                        src: img.src,
                        sx: args[1], sy: args[2],
                        sWidth: args[3], sHeight: args[4],
                        dx: args[5], dy: args[6],
                        dWidth: args[7], dHeight: args[8]
                    });
                }
            }
        } catch (err) {
            console.error("drawImage hook error:", err);
        }

        return original.apply(this, args);
    };

    window.__drawCalls = logs;
    console.log("HOOK ĐÃ CÀI: Dữ liệu sẽ lưu trong window.__drawCalls");
})();
