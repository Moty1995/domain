package phash;

import java.awt.Graphics2D;
import java.awt.color.ColorSpace;
import java.awt.image.BufferedImage;
import java.awt.image.ColorConvertOp;
import java.io.File;
import java.io.FileInputStream;
// import java.io.FileNotFoundException;
// import java.io.InputStream;
import java.io.FileNotFoundException;
import java.io.IOException;

import javax.imageio.ImageIO;
/*
* function: 1. Calculate perceptual hash value of pictures with DCT
* 			2. Calculate the difference between two pHash value with Hamming Distance 
* reference: https://blog.csdn.net/sunhuaqiang1/article/details/70232679
*            http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html
*/

public class PHash {

    private int size = 32;
    private int smallerSize = 8;

    public PHash() {
        initCoefficients();
    }
    
    public PHash(int size, int smallerSize) {
        this.size = size;
        this.smallerSize = smallerSize;

        initCoefficients();
    }
    
// Use hamming distance to calculate the difference
    public static int distance(String s1, String s2) {
        int counter = 0;
        for (int k = 0; k < s1.length();k++) {
            if(s1.charAt(k) != s2.charAt(k)) {
                counter++;
            }
        }
        return counter;
    }
    
    public static BufferedImage getImg(String path) {
    	BufferedImage img = null;
    	try {
			img = ImageIO.read(new FileInputStream(new File(path)));
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
    	return img;
    }

    // Returns a 'binary string' (like. 001010111011100010) which is easy to do a hamming distance on.
    public String getHash(String path) {
    	BufferedImage img = getImg(path);

/* 1. Reduce size
Like Average Hash, pHash starts with a small image, however, the image size is not 8x8, but 32x32.
This is really done to simplify the DCT computation and not because it is needed to reduce the high frequencies.
*/
        img = resize(img, size, size);

/* 2. Reduce color
The image is reduced to a grayscale just to further simplify the number of computations.
*/
        img = grayscale(img);

        double[][] vals = new double[size][size];

        for (int x = 0; x < img.getWidth(); x++) {
            for (int y = 0; y < img.getHeight(); y++) {
                vals[x][y] = getBlue(img, x, y);
            }
        }

/* 3. Compute the DCT
The DCT(Discrete Cosine Transform) separates the image into a collection of frequencies and scalars. While JPEG uses an 8x8 DCT, this algorithm uses a 32x32 DCT.
*/
        double[][] dctVals = applyDCT(vals);

/* 4. Reduce the DCT.
While the DCT is 32x32, just keep the top-left 8x8. Those represent the lowest frequencies in the picture.
*/
/* 5. Compute the average value.
Like the Average Hash, compute the mean DCT value (using only the 8x8 DCT low-frequency values and excluding the first term since the DC coefficient can be significantly different from the other values and will throw off the average).
*/
        double total = 0;

        for (int x = 0; x < smallerSize; x++) {
            for (int y = 0; y < smallerSize; y++) {
                total += dctVals[x][y];
            }
        }
        total -= dctVals[0][0];

        double avg = total / (double) ((smallerSize * smallerSize) - 1);

/* 6. Further reduce the DCT.
Set the 64 hash bits to 0 or 1
depending on whether each of the 64 DCT values is above or below the average value. The result doesn't tell us the
actual low frequencies; it just tells us the very-rough relative scale of the frequencies to the mean. The result
will not vary as long as the overall structure of the image remains the same; this can survive gamma and color histogram adjustments without a problem.
*/
        String hash = "";

        for (int x = 0; x < smallerSize; x++) {
            for (int y = 0; y < smallerSize; y++) {
            	hash += (dctVals[x][y] > avg?"1":"0");
            }
        }

        return hash;
    }

    public BufferedImage resize(BufferedImage image, int width, int height) {
        BufferedImage resizedImage = new BufferedImage(width, height, BufferedImage.TYPE_INT_ARGB);
        Graphics2D g = resizedImage.createGraphics();
        g.drawImage(image, 0, 0, width, height, null);
        g.dispose();
        return resizedImage;
    }

    private ColorConvertOp colorConvert = new ColorConvertOp(ColorSpace.getInstance(ColorSpace.CS_GRAY), null);

    public BufferedImage grayscale(BufferedImage img) {
        colorConvert.filter(img, img);
        return img;
    }

    public static int getBlue(BufferedImage img, int x, int y) {
        return (img.getRGB(x, y)) & 0xff;
    }

// DCT function
// reference： http://stackoverflow.com/questions/4240490/problems-with-dct-and-idct-algorithm-in-java

    private double[] c;
    public void initCoefficients() {
        c = new double[size];

        for (int i=1;i<size;i++) {
            c[i]=1;
        }
        c[0]=1/Math.sqrt(2.0);
    }

    public double[][] applyDCT(double[][] f) {
        int N = size;

        double[][] F = new double[N][N];
        for (int u=0;u<N;u++) {
            for (int v=0;v<N;v++) {
                double sum = 0.0;
                for (int i=0;i<N;i++) {
                    for (int j=0;j<N;j++) {
                        sum+=Math.cos(((2*i+1)/(2.0*N))*u*Math.PI)*Math.cos(((2*j+1)/(2.0*N))*v*Math.PI)*(f[i][j]);
                    }
                }
                sum*=((c[u]*c[v])/4.0);
                F[u][v] = sum;
            }
        }
        return F;
    }

// Transform the binary string to hex string
// reference: https://blog.csdn.net/evangel_z/article/details/7527983
    public static String binaryString2hexString(String bString) {
    	if (bString == null || bString.equals("") || bString.length() % 8 != 0) {
    		return null;
    	}
    	StringBuffer tmp=new StringBuffer();
    	int iTmp = 0;
    	for (int i = 0; i < bString.length(); i += 4) {
    		iTmp = 0;
    		for (int j = 0; j < 4; j++) {
    			iTmp += Integer.parseInt(bString.substring(i + j, i + j + 1)) << (4 - j - 1);
    		}
    		tmp.append(Integer.toHexString(iTmp));
    	}
    	return tmp.toString();
    }

// Transform the hex string to binary string
   	public static String hexString2binaryString(String hexString)
   	{
   		if (hexString == null || hexString.length() % 2 != 0)
   			return null;
   		String bString = "", tmp;
   		for (int i = 0; i < hexString.length(); i++)
   		{
   			tmp = "0000"
   					+ Integer.toBinaryString(Integer.parseInt(hexString
   							.substring(i, i + 1), 16));
   			bString += tmp.substring(tmp.length() - 4);
   		}
   		return bString;
   	}
    
    public static void main(String[] args) {
    	PHash p = new PHash();
    	String bit1 = p.getHash("D:\\Files\\Course\\772\\Final\\Pictures\\0844.png");
    	String bit2 = p.getHash("D:\\Files\\Course\\772\\Final\\Pictures\\0917.png");
        String hex1 = binaryString2hexString(bit1);
        String hex2 = binaryString2hexString(bit2);
        System.out.println(hex1);
    	System.out.println(hex2);
        System.out.println(distance(bit1,bit2));
    }

}
