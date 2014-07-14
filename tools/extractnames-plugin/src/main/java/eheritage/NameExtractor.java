package eheritage;

import java.io.InputStream;
import java.util.List;

import opennlp.tools.namefind.NameFinderME;
import opennlp.tools.namefind.TokenNameFinderModel;
import opennlp.tools.util.Span;

import org.apache.commons.lang3.StringUtils;

import com.google.common.collect.Lists;

public class NameExtractor {

  private TokenNameFinderModel model;

  public NameExtractor() {
    try (InputStream in = this.getClass().getResourceAsStream("/en-ner-person.bin")) {
      model = new TokenNameFinderModel(in);
    } catch(Exception e) {
      throw new RuntimeException("failed to initialize model", e);
    }
  }

  public List<String> getNames(String text) {
    List<String> names = Lists.newArrayList();
    NameFinderME nameFinder = new NameFinderME(model);
    String[] sentences = StringUtils.split(text, " .");
    Span nameSpans[] = nameFinder.find(sentences);
    for(Span span : nameSpans) {
      if(span != null) {
        String name = StringUtils.join(sentences, ' ', span.getStart(), span.getEnd());
        names.add(name);
      }
    }
    return names;
  }
}
