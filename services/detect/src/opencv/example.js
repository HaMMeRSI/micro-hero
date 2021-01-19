const getDetection = require('./get-detection');
const loadOpenCv = require('./loader');

loadOpenCv()
    .then(() => getDetection(`${__dirname}/batman.jpg`))
    .then(detection => console.log(`detection: ${detection}`))
    .catch(console.error);
