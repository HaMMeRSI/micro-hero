const { loadImage } = require('canvas');

/*
    @param buffer: Buffer | path to local file
    @return: Promise<detection array>
    should call loadOpenCv from loader before first request
 */
async function getDetection(buffer) {
    const gray = new cv.Mat();
    const image = await loadImage(buffer);
    const src = cv.imread(image);

    try {
        cv.cvtColor(src, gray, cv.COLOR_RGBA2GRAY, 0);
        const faces = new cv.RectVector();
        const faceCascade = new cv.CascadeClassifier();
        faceCascade.load('./haarcascade_frontalface_default.xml');
        faceCascade.detectMultiScale(gray, faces, 1.3, 5);
        const { x, y, width, height } = faces.get(0);
        return [y, x + width, y + height, x];
    } catch (e) {
        console.error(e);
        throw new Error('Face not detected')
    } finally {
        gray.delete();
        src.delete();
    }
}

module.exports = getDetection;