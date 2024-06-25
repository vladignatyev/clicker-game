window.hyperdiv.registerPlugin("time", (ctx) => {

    let interval = setInterval(() => {
        ctx.updateProp("count", 1);
    }, 1000);
});