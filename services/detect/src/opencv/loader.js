const {existsSync, mkdirSync} = require("fs");
const path = require('path');


const { Canvas, Image, ImageData } = require('canvas');
const {JSDOM} = require('jsdom');


function loadOpenCv(rootDir = './work', localRootDir = path.resolve(__dirname)) {
    if (global.Module && global.Module.onRuntimeInitialized && global.cv && global.cv.imread) {
        return Promise.resolve()
    }

    return new Promise(resolve => {
        installDom()
        global.Module = {
            onRuntimeInitialized() {
                cv.FS.chdir(rootDir)
                resolve()
            },
            preRun() {
                const FS = global.Module.FS

                if (!FS.analyzePath(rootDir).exists) {
                    FS.mkdir(rootDir);
                }

                if (!existsSync(localRootDir)) {
                    mkdirSync(localRootDir, {recursive: true});
                }
                FS.mount(FS.filesystems.NODEFS, {root: localRootDir}, rootDir);
            }
        };
        global.cv = require('./opencv.js')
    });
}

function installDom() {
    const dom = new JSDOM();
    global.document = dom.window.document;
    global.Image = Image;
    global.HTMLCanvasElement = Canvas;
    global.ImageData = ImageData;
    global.HTMLImageElement = Image;
}

module.exports = loadOpenCv;