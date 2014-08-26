/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/*
This files expects to be given a file lines where each line consists the tweet and "time of tweet"
seperated by |","| time format : seconds since epoch
*/
package graphhashtagrecommendor;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

/**
 *
 * @author vedratn
 */
public class GraphHashtagRecommendor {
    static ArrayList <TweetPair> fullTweets = new ArrayList<TweetPair>();
    static ArrayList<String> fullHashtags = new ArrayList<String>();
    static ArrayList <String> fullTweetsTest = new ArrayList<String>();
    static ArrayList<HashSet<String>> fullHashtagsTest = new ArrayList<HashSet<String>>();
    static List<List<String>> tweets = new ArrayList<List<String>>();
    static Map<String, Integer> indexMap = new HashMap<String, Integer>();
    static Map<Integer, String> reverseIndexMap = new HashMap<Integer, String>();
    static Set<Integer> isHashtag = new HashSet<Integer>();
    static Map<String, Integer> IDF = new HashMap<String, Integer>();
    static Integer[] tagHits = new Integer[4];
    static Integer foldValue = 0;

    static UndirectedGraph tweetGraph;
    
    
    static float filterThreshold;
    static int bfsThreshold;
    static int topKHashtags;
    
    static void filterTweets(){
        int N;
        N = fullTweets.size();
        System.out.println(N+" is the size of fulltweets");
        String[] tweetWords;
        for(TweetPair tp:fullTweets){
            tweetWords = tp.tweet.split("\\s+");
            for(String token: tweetWords){
                if(IDF.containsKey(token)){
                    IDF.put(token, IDF.get(token)+1);
                }else{
                    IDF.put(token, 1);
                }
            }
        }
        
        float factor;
        for(TweetPair tp:fullTweets){
            List<String>s=new ArrayList<String>();
            
            tweetWords = tp.tweet.split("\\s+");
            for(String token: tweetWords){
                factor = (float)N/IDF.get(token);
                if(factor >= filterThreshold){
                    s.add(token);
                }else{
                    //System.out.println(token +" is rejectedd because it has factor = "+factor);
                }
            }
            tweets.add(s);
        }
    }
    
    static void insertIntoGraph(){
        int index = 0;
        for(List<String>l:tweets){
            for(String s:l){
                if(!indexMap.containsKey(s)){
                    indexMap.put(s,index);
                    reverseIndexMap.put(index,s);
                    if(s.charAt(0) == '#') isHashtag.add(index);
                    index++;
                }
            }
        }
        int size = indexMap.size();
        tweetGraph=new UndirectedGraph();
        for(int i = 0; i < size; i++){
            tweetGraph.addNode(i);
        }
    }
    
    static void findConnections(){
        int index1, index2;
        for(List<String>l:tweets){
            for(int i = 0; i < l.size(); i++){
                for(int j = i+1; j < l.size(); j++){
                    index1 = indexMap.get(l.get(i));
                    index2 = indexMap.get(l.get(j));
                    if(index1 != index2){
                        if(tweetGraph.edgeExists(index1, index2)){
                            tweetGraph.addWeight(index1, index2);
                        }else{
                            tweetGraph.addEdge(index1, index2);
                        }
                    }
                }
            }
        }
        // System.out.println("Intex of Kindle2 is :"+indexMap.get("kindle2"));
        
        tweetGraph.normalize();
        /*
        System.out.println("AAYA");
        for(List<String>l:tweets){
            for(int i = 0; i < l.size(); i++){
                for(int j = i+1; j < l.size(); j++){
                    index1 = indexMap.get(l.get(i));
                    index2 = indexMap.get(l.get(j));
                    String key = Integer.toString(Math.min(index1, index2))+"#"+Integer.toString(Math.max(index1, index2));
                    System.out.println(l.get(i)+":"+l.get(j)+"=>"+tweetGraph.weightGraph.get(key)
                            +":"+tweetGraph.vertexWeight.get(index1)+":"+tweetGraph.vertexWeight.get(index2)
                    );
                }
            }
        }*/
     
    }
    
    // Use heap to make it fast
    // http://www.michaelpollmeier.com/selecting-top-k-items-from-a-list-efficiently-in-java-groovy/
    static ArrayList<Integer> sortByValue(Map<Integer, Double> map) {
        LinkedList<Map.Entry<Integer,Double>> list = new LinkedList(map.entrySet());
        Collections.sort(list, new Comparator() {
            public int compare(Object o1, Object o2) {
                return ((Comparable) ((Map.Entry<Integer,Double>) (o2)).getValue())
                        .compareTo(((Map.Entry<Integer,Double>) (o1)).getValue());
            }
        });

        ArrayList<Integer> result = new ArrayList<Integer>();
        for (Iterator it = list.iterator(); it.hasNext();) {
            Map.Entry<Integer,Double> entry = (Map.Entry<Integer,Double>)it.next();
            result.add(entry.getKey());
        }
        return result;
    }
    
    static HashMap<Integer,Double> filterScoresForHashtags(HashMap<Integer,Double> scores){
        HashMap<Integer,Double> hashtagScores = new HashMap<Integer,Double>();
        for(Map.Entry<Integer,Double>entry: scores.entrySet()){
            if(isHashtag.contains(entry.getKey())){
                hashtagScores.put(entry.getKey(), entry.getValue());
            }
        }
        return hashtagScores;
    }
    
    static ArrayList<Integer> giveHashTags(String tw){
        String[] tweetWords = tw.split("\\s+");
        HashMap<Integer,Double> myScore = new HashMap<Integer,Double>();
        for (String token: tweetWords) {
            if(indexMap.containsKey(token)){
                tweetGraph.scoreTerm(indexMap.get(token),myScore,bfsThreshold);
            }
        }
        myScore = filterScoresForHashtags(myScore);
        return sortByValue(myScore);
    }
    
    static void insertTweetsAndFilter() throws FileNotFoundException, IOException{
        String tweetsFile = "tweets";
        String hashtagFile = "hashtags";
        BufferedReader tweetsReader;
        tweetsReader = new BufferedReader(new FileReader(tweetsFile));
        BufferedReader hashtagsReader;
        hashtagsReader = new BufferedReader(new FileReader(hashtagFile));
        String tweetLine, hashtagLine;          
        int ti;
        int tweetNum = 0;
        while ((tweetLine = tweetsReader.readLine()) != null) {
            hashtagLine = hashtagsReader.readLine();
            if(tweetNum % 5 == foldValue){
                fullTweetsTest.add(tweetLine);
                fullHashtagsTest.add(new HashSet<String>(Arrays.asList(hashtagLine.trim().split("\\s+"))));
            } else {
                tweetLine += " " + hashtagLine;
                // not considering the time as of now
                ti = 4;
                tweetLine = tweetLine.trim();
                fullTweets.add(new TweetPair(tweetLine,ti));
            }
            tweetNum++;
        }
        tweetsReader.close();
        hashtagsReader.close();  
        filterTweets();   
    }
    
    public static void updateHits(ArrayList<Integer> sortedTags, HashSet<String> originalTags) {
        int i;
        for(i = 0; i<sortedTags.size(); i++){
            if(originalTags.contains(reverseIndexMap.get(sortedTags.get(i)))){
                System.out.println("Found " + reverseIndexMap.get(sortedTags.get(i)));
                break;
            }
        }
        if(i == originalTags.size()) return;
        if(i < 5) tagHits[0]++;
        if(i < 10) tagHits[1]++;
        if(i < 15) tagHits[2]++;
        if(i < 20) tagHits[3]++;
    }
    
    public static String removeHashTagsFromTestTweet(String tweet, HashSet<String> tags){
        for(String s: tags){
            s = s.substring(1);
            tweet = tweet.replaceFirst(Pattern.quote(s), "");
        }
        return tweet;
    }
    
    public static void main(String[] args) throws IOException {
        filterThreshold = 0;
        foldValue = 0;
        bfsThreshold = 2;
        topKHashtags = 20;

        insertTweetsAndFilter();
        insertIntoGraph();
        findConnections();
        
        for(int i = 0 ; i<4; i++) tagHits[i] = 0;
        System.out.printf("Total Test Tweets = %d\n", fullTweetsTest.size());
        String testTweet;
        // test on test tweets, five fold
        for(int i = 0; i<20; i++){
            testTweet = removeHashTagsFromTestTweet(fullTweetsTest.get(i), fullHashtagsTest.get(i));
            System.out.println(testTweet);
            System.out.printf("Testing Tweet %d\n", i);
            updateHits(giveHashTags(testTweet), fullHashtagsTest.get(i));
        }
        System.out.printf("%d %d %d %d\n", tagHits[0], tagHits[1], tagHits[2], tagHits[3]);
    } 
}